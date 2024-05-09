import time
import datetime

#Algorithm
from ..algorithms import (
    GeneticAlgorithm,
    GeneticLocalSearch
)

from ..config_schema import ScheduleConfiguration
#Model
from scheduling_data.models import Solution, ScheduleData, Semester

from django.db import transaction

from scheduling_data.utils import signals

class SolutionGenerator:
    def __init__(self, data: ScheduleConfiguration):
        # self.config = ScheduleConfiguration.from_data(data)
        self.config = data
        self.algorithm: GeneticAlgorithm = self.configure_algorithm()
        self.best_chromosome = None
        self.time_elapsed = 0
        
        self.created_solution = None
        
    @classmethod
    def from_data(cls, data: dict):
        return cls(ScheduleConfiguration.from_data(data))
        
    def configure_algorithm(self):
        algorithm = self.config.get_main_algorithm()
        if algorithm == "genetic_algorithm":
            return self.configure_genetic_algorithm()
        elif algorithm == "genetic_local_search":
            return self.configure_genetic_local_search_algorithm()
        else:
            raise ValueError(f"Invalid algorithm: {algorithm}")
        
    def configure_genetic_algorithm(self):
        config = self.config.get_algorithm_config()
        return GeneticAlgorithm.create(config=config)
    
    def configure_genetic_local_search_algorithm(self):
        main_config = self.config.get_algorithm_config()
        local_search_config = self.config.get_local_search_config()
        return GeneticLocalSearch.create(main_config, local_search_config)
    
    def generate_solution(self) -> Solution:
        """Generates a timetabling solution using the configured algorithm.

        Raises:
            e: Any exception that occurs during the solution generation.

        Returns:
            Solution: The generated solution data.
        """
        solution = self.created_solution or self.create_solution()
        try:
            self.algorithm.run()
            self.best_chromosome = self.algorithm.log['best_chromosome']
            self.create_schedule_data(solution)
            self.update_solution(solution)
        except Exception as e:
            self.update_solution(solution, status=Solution.Status.FAILED)
            raise e
        self.created_solution = None
        return solution
    
    def create_solution(self) -> Solution:
        """Creates a new solution object in the database. For storing configuration and progress data.

        Returns:
            Solution: The created solution object.
        """
        data = self.config
        
        solution = Solution()
        semester_id = data['semester']
        semester_instance = Semester.objects.get(pk=semester_id)
        solution.name = "Solution " + str(time.ctime())
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
        self.created_solution = solution
        
        signals.notify_task(solution)
        return solution
    
    def update_solution(self, solution: Solution, status=Solution.Status.COMPLETED):
        solution.status = status
        solution.best_fitness = self.best_chromosome.fitness
        solution.time_elapsed = self.algorithm.log['time_elapsed']
        solution.gene_count = len(self.best_chromosome)
        solution.save()
        
        signals.notify_task(solution)
        return solution
    
    def create_schedule_data(self, solution: Solution):
        schedule_data_list = []
        for gene in self.best_chromosome:
            schedule_data_list.append(ScheduleData(
                solution=solution,
                laboratory_id=gene['laboratory'],
                module_id=gene['module'],
                chapter_id=gene['chapter'],
                group_id=gene['group'],
                assistant_id=gene['assistant'],
                date= datetime.datetime.fromtimestamp(gene['time_slot'].date, tz=datetime.timezone.utc),
                day=gene['time_slot'].day,
                shift=gene['time_slot'].shift
            ))

        with transaction.atomic():
            ScheduleData.objects.bulk_create(schedule_data_list)
    
    
