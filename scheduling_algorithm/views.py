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
    GeneticLocalSearch
)
from .algorithms.local_search import (
    TabuSearch,
    SimulatedAnnealing
)

from .factory import Factory

#Fitness function
from .fitness_function import (
    FitnessManager,
    AssistantDistributionFitness,
    GroupAssignmentConflictFitness
)

#operator
from .operator.selection import (
    SelectionManager,
    RouletteWheelSelection,
    TournamentSelection,
    ElitismSelection
)
from .operator.crossover import (
    CrossoverManager, 
    SinglePointCrossover, 
    TwoPointCrossover, 
    UniformCrossover
)
from .operator.mutation import (
    MutationManager, 
    SwapMutation, 
    ShiftMutation, 
    RandomMutation

)
from .operator.repair import (
    RepairManager, 
    TimeSlotRepair
)

#Neighborhood for local search
from .algorithms.neighborhood import RandomSwapNeighborhood

#Tabu list
from .structure import Chromosome, TabuList

#Json schema for configuration, used for validation and default value

from .config_schema import ScheduleConfiguration

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

    def configure_fitness_manager(self, fitness_config):
        group_assignment_conflict_fitness = GroupAssignmentConflictFitness().configure(
            max_threshold=fitness_config['group_assignment_conflict'].get('max_threshold'),
            conflict_penalty=fitness_config['group_assignment_conflict'].get('conflict_penalty')
            )
        
        assistant_distribution_fitness = AssistantDistributionFitness().configure(
            max_group_threshold=fitness_config['assistant_distribution'].get('max_group_threshold'),
            max_shift_threshold=fitness_config['assistant_distribution'].get('max_shift_threshold'),
            group_penalty=fitness_config['assistant_distribution'].get('group_penalty'),
            shift_penalty=fitness_config['assistant_distribution'].get('shift_penalty')
            )
        
        fitness_manager = FitnessManager([group_assignment_conflict_fitness, assistant_distribution_fitness])
        return fitness_manager
    
    def configure_selection_manager(self, selection_config):
        selection = []
        if selection_config['roulette_wheel']:
            selection.append(RouletteWheelSelection())

        if selection_config['tournament']:
            tournament = TournamentSelection()
            tournament.configure(tournament_size=selection_config.get('tournament_size'))
            selection.append(tournament)

        if selection_config['elitism']:
            elitism = ElitismSelection()
            elitism.configure(elitism_size=1)
            selection.append(elitism)

        if not selection:
            selection.append(RouletteWheelSelection())

        selection_manager = SelectionManager(selection)
        return selection_manager
    
    def configure_crossover_manager(self, crossover_config):
        crossover = []
        if crossover_config['single_point']:
            crossover.append(SinglePointCrossover())

        if crossover_config['two_point']:
            crossover.append(TwoPointCrossover())

        if crossover_config['uniform']:
            uniform = UniformCrossover()
            uniform.configure(uniform_probability=crossover_config.get('uniform_probability'))
            crossover.append(uniform)

        if not crossover:
            crossover.append(SinglePointCrossover())

        crossover_manager = CrossoverManager(crossover).configure(crossover_probability=crossover_config.get('crossover_probability'))
        return crossover_manager
    
    def configure_mutation_manager(self, mutation_config):
        mutation = []
        if mutation_config['swap']:
            mutation.append(SwapMutation())

        if mutation_config['shift']:
            mutation.append(ShiftMutation())

        if mutation_config['random']:
            mutation.append(RandomMutation())

        if not mutation:
            mutation.append(SwapMutation())

        mutation_manager = MutationManager(mutation).configure(mutation_probability=mutation_config.get('mutation_probability'))
        return mutation_manager
    
    def configure_repair_manager(self, repair_config):
        repair = []
        if repair_config['time_slot']:
            repair.append(TimeSlotRepair())

        if not repair:
            repair.append(TimeSlotRepair())

        repair_manager = RepairManager(repair)
        return repair_manager
    
    def configure_neighborhood(self, neighborhood_config):
        if neighborhood_config['algorithm'] == "random_swap":
            neighborhood = RandomSwapNeighborhood()
            neighborhood.configure(neighborhood_size=neighborhood_config.get('neighborhood_size'))
        else:
            neighborhood = RandomSwapNeighborhood()
            neighborhood.configure(neighborhood_size=neighborhood_config.get('neighborhood_size'))
        return neighborhood

    def configure_local_search(self, local_search_config, fitness_manager, neighborhood):

        if local_search_config['algorithm'] == "tabu_search":
            config = local_search_config.get('tabu_search')
            local_search = TabuSearch()
            tabu_list = TabuList(tabu_list_size=config.get('tabu_list_size'))
            local_search.configure(fitness_manager=fitness_manager, 
                                    neighborhood=neighborhood, 
                                    tabu_list=tabu_list,
                                    max_iteration=config.get('max_iteration'),
                                    max_time=config.get('max_time'),
                                    max_iteration_without_improvement=config.get('max_iteration_without_improvement'),
                                    max_time_without_improvement=config.get('max_time_without_improvement'))

        elif local_search_config['algorithm'] == "simulated_annealing":
            config = local_search_config.get('simulated_annealing')
            local_search = SimulatedAnnealing()
            local_search.configure(fitness_manager=fitness_manager,
                                    neighborhood=neighborhood, 
                                    initial_temperature=config.get('initial_temperature'),
                                    cooling_rate=config.get('cooling_rate'),
                                    max_iteration=config.get('max_iteration'),
                                    max_time=config.get('max_time') 
                                    )
            
        else:
            return Response({"error": "No local search is selected"}, status=status.HTTP_400_BAD_REQUEST)
            
        return local_search
    
    def post(self, request):
        data = ScheduleConfiguration.from_data(request.data)
        data.save("last_config.json")
        
        # Initialize the configuration
        factory = Factory()
        fitness_manager = self.configure_fitness_manager(data.get_fitness_config())
        selection_manager = self.configure_selection_manager(data.get_selection_config())
        crossover_manager = self.configure_crossover_manager(data.get_crossover_config())
        mutation_manager = self.configure_mutation_manager(data.get_mutation_config())
        repair_manager = self.configure_repair_manager(data.get_repair_config())
        elitism = ElitismSelection()
        elitism_size = data.get_elitism_size()

        # Initialize the algorithm
        if data.is_genetic_algorithm():
            algorithm = GeneticAlgorithm()
            algorithm.configure(factory=factory, 
                                fitness_manager=fitness_manager, 
                                selection_manager=selection_manager, 
                                crossover_manager=crossover_manager, 
                                mutation_manager=mutation_manager, 
                                repair_manager=repair_manager, 
                                elitism_selection=elitism,
                                elitism_size= elitism_size)
            
        elif data.is_genetic_local_search():
            # Configure the local search
            neighborhood = self.configure_neighborhood(data.get_neighborhood_config())
            local_search = self.configure_local_search(data.get_local_search(), fitness_manager, neighborhood)
            # Main Algorithm   
            algorithm = GeneticLocalSearch()
            algorithm.configure(factory=factory,
                                fitness_manager=fitness_manager,
                                selection_manager=selection_manager,
                                crossover_manager=crossover_manager,
                                mutation_manager=mutation_manager,
                                repair_manager=repair_manager,
                                elitism_selection=elitism,
                                elitism_size= elitism_size,
                                local_search=local_search)
            
        else:
            return Response({"error": "No algorithm is selected"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the solution
        solution = self.create_solution(data)

        # Run the algorithm
        try:
            best_chromosome: Chromosome = algorithm.run(max_iteration=data.get_max_iteration(),
                                                        population_size=data.get_population_size())
            # Update the solution
            solution = self.update_solution(solution, best_chromosome, algorithm, status="Saving")
            # Create the schedule data
            self.create_schedule_data(solution, best_chromosome)
            # Update the solution
            solution.status = "Completed"
            solution.save()
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
