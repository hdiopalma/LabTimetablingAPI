from rest_framework.permissions import AllowAny
import time

from django.db import transaction


# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

#Model
from scheduling_data.models import Solution, ScheduleData, Semester

#Algorithm
from .algorithms import (
    GeneticAlgorithm,
)
#Tabu list
from .structure import Chromosome

#Json schema for configuration, used for validation and default value

from .config_schema import ScheduleConfiguration

from .utils.solution_generator import SolutionGenerator

class GenerateTimetabling(APIView):
    permission_classes = [AllowAny]

    def create_solution(self, data: ScheduleConfiguration):
        solution = Solution()
        semester_id = data['semester']
        semester_instance = Semester.objects.get(pk=semester_id)
        solution.name = "Generated on " + str(time.ctime())
        solution.semester = semester_instance
        solution.fitness = data.get_fitness_config()
        solution.selection = data.get_selection_config()
        solution.crossover = data.get_crossover_config()
        solution.mutation = data.get_mutation_config()
        solution.repair = data.get_repair_config()
        solution.neighborhood = data.get_neighborhood_config()
        solution.algorithm = data.get_algorithm()
        solution.local_search = data.get_local_search()
        solution.max_iteration = data.get_max_iteration()
        solution.population_size = data.get_population_size()
        solution.elitism_size = data.get_elitism_size()
        solution.save()
        return solution
    
    def update_solution(self, solution: Solution, best_chromosome: Chromosome, algorithm: GeneticAlgorithm, status="Completed"):
        solution.status = status
        # solution.iteration_log = algorithm.log['iteration_log']
        solution.best_fitness = best_chromosome.fitness
        solution.time_elapsed = algorithm.log['time_elapsed']
        # solution.best_solution = best_chromosome.to_json()
        solution.gene_count = len(best_chromosome)
        solution.save()
        return solution
    
    def create_schedule_data(self, solution: Solution, best_chromosome: Chromosome):
        schedule_data_list = []
        for gene in best_chromosome:
            schedule_data_list.append(ScheduleData(
                solution=solution,
                laboratory_id=gene['laboratory'],
                module_id=gene['module'],
                chapter_id=gene['chapter'],
                group_id=gene['group'],
                assistant_id=gene['assistant'],
                date=gene['time_slot'].date,
                day=gene['time_slot'].day,
                shift=gene['time_slot'].shift
            ))

        with transaction.atomic():
            ScheduleData.objects.bulk_create(schedule_data_list)
    
    def post(self, request):
        data = ScheduleConfiguration.from_data(request.data) # Parse and validate the data
        algorithm = SolutionGenerator(data).configure_algorithm()
        solution = self.create_solution(data)
        # Run the algorithm
        try:
            # best_chromosome: Chromosome = algorithm.run(max_iteration=data.get_max_iteration(),
            #                                             population_size=data.get_population_size())
            
            best_chromosome: Chromosome = algorithm.run()
            # Update the solution
            print("Solution generated, saving the solution")
            solution = self.update_solution(solution, best_chromosome, algorithm, status="Saving")
            # Create the schedule data
            self.create_schedule_data(solution, best_chromosome)
            # Update the solution
            solution.status = "Completed"
            solution.save()
            print("Solution saved")
            return Response({
                "best_fitness": best_chromosome.fitness,
                "time_elapsed": algorithm.log['time_elapsed'],
                "best_solution": best_chromosome.to_json(),
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            #set the status to error
            solution.status = "Error"
            solution.save()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
