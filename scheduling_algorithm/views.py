from django.shortcuts import render

from rest_framework.permissions import AllowAny

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from scheduling_algorithm.algorithms.global_search.genetic_algorithm import GeneticAlgorithm
from scheduling_algorithm.algorithms.hybrid.genetic_local_search import GeneticLocalSearch
from scheduling_algorithm.algorithms.local_search.simulated_annealing import SimulatedAnnealing
from scheduling_algorithm.algorithms.local_search.tabu_search import TabuSearch 

from scheduling_algorithm.factory.factory import Factory

from scheduling_algorithm.fitness_function import FitnessManager, AssistantDistributionFitness, GroupAssignmentConflictFitness

#operator
from scheduling_algorithm.operator.selection import SelectionManager, RouletteWheelSelection, TournamentSelection, ElitismSelection
from scheduling_algorithm.operator.crossover import CrossoverManager, SinglePointCrossover, TwoPointCrossover, UniformCrossover
from scheduling_algorithm.operator.mutation import MutationManager, SwapMutation, ShiftMutation, RandomMutation
from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair

#Neighborhood for local search
from scheduling_algorithm.algorithms.neighborhood import RandomSwapNeighborhood

#Tabu list
from scheduling_algorithm.structure import Chromosome, TabuList

class GenerateTimetabling(APIView):
    permission_classes = [AllowAny]

    def configure_fitness_manager(self, data):
        group_assignment_conflict_fitness = GroupAssignmentConflictFitness().configure(max_threshold=data['fitness'].get('max_threshold', 3),
                                                                                    conflict_penalty=data['fitness'].get('conflict_penalty', 1))
        
        assistant_distribution_fitness = AssistantDistributionFitness().configure(max_group_threshold=data['fitness'].get('max_group_threshold', 15),
                                                                                max_shift_threshold=data['fitness'].get('max_shift_threshold', 50),
                                                                                group_penalty=data['fitness'].get('group_penalty', 1),
                                                                                shift_penalty=data['fitness'].get('shift_penalty', 1))
        
        fitness_manager = FitnessManager([group_assignment_conflict_fitness, assistant_distribution_fitness])
        return fitness_manager
    
    def configure_selection_manager(self, data):
        selection = []
        if data['selection']['roulette_wheel']:
            selection.append(RouletteWheelSelection())

        if data['selection']['tournament']:
            tournament = TournamentSelection()
            tournament.configure(tournament_size=data.get('tournament_size', 2))
            selection.append(tournament)

        if data['selection']['elitism']:
            elitism = ElitismSelection()
            elitism.configure(elitism_size=1)
            selection.append(elitism)

        if selection == []:
            selection.append(RouletteWheelSelection())

        selection_manager = SelectionManager(selection)
        return selection_manager
    
    def configure_crossover_manager(self, data):
        crossover = []
        if data['crossover']['single_point']:
            crossover.append(SinglePointCrossover())

        if data['crossover']['two_point']:
            crossover.append(TwoPointCrossover())

        if data['crossover']['uniform']:
            uniform = UniformCrossover()
            uniform.configure(uniform_probability=data['crossover'].get('uniform_probability', 0.5))
            crossover.append(uniform)

        if crossover == []:
            crossover.append(SinglePointCrossover())

        crossover_manager = CrossoverManager(crossover).configure(crossover_probability=data['crossover'].get('crossover_probability', 0.1))
        return crossover_manager
    
    def configure_mutation_manager(self, data):
        mutation = []
        if data['mutation']['swap']:
            mutation.append(SwapMutation())

        if data['mutation']['shift']:
            mutation.append(ShiftMutation())

        if data['mutation']['random']:
            mutation.append(RandomMutation())

        if mutation == []:
            mutation.append(SwapMutation())

        mutation_manager = MutationManager(mutation).configure(mutation_probability=data['mutation'].get('mutation_probability', 0.1))
        return mutation_manager
    
    def configure_repair_manager(self, data):
        repair = []
        if data['repair']['time_slot']:
            repair.append(TimeSlotRepair())

        if repair == []:
            repair.append(TimeSlotRepair())

        repair_manager = RepairManager(repair)
        return repair_manager
    
    def configure_neighborhood(self, data):
        if data['neighborhood']['random_swap']:
            neighborhood = RandomSwapNeighborhood()
            neighborhood.configure(neighborhood_size=data['neighborhood'].get('neighborhood_size', 100))
        else:
            neighborhood = RandomSwapNeighborhood()
            neighborhood.configure(neighborhood_size=data['neighborhood'].get('neighborhood_size', 100))
        return neighborhood

    def configure_local_search(self, data, fitness_manager, neighborhood):
        if data['local_search']['simulated_annealing']:
            local_search = SimulatedAnnealing()
            local_search.configure(fitness_manager=fitness_manager,
                                    neighborhood=neighborhood, 
                                    initial_temperature=data['local_search'].get('initial_temperature', 100),
                                    cooling_rate=data['local_search'].get('cooling_rate', 0.1),
                                    max_iteration=data['local_search'].get('max_iteration', 1000),
                                    max_time=data['local_search'].get('max_time', 60))
            
        elif data['local_search']['tabu_search']:
            local_search = TabuSearch()
            tabu_list = TabuList(tabu_list_size=data['local_search'].get('tabu_list_size', 50))
            local_search.configure(fitness_manager=fitness_manager, 
                                    neighborhood=neighborhood, 
                                    tabu_list=tabu_list,
                                    max_iteration=data['local_search'].get('max_iteration', 1000),
                                    max_time=data['local_search'].get('max_time', 60),
                                    max_iteration_without_improvement=data['local_search'].get('max_iteration_without_improvement', 100),
                                    max_time_without_improvement=data['local_search'].get('max_time_without_improvement', 5))
            
        else:
            return Response({"error": "No local search is selected"}, status=status.HTTP_400_BAD_REQUEST)
            
        return local_search
    
    def post(self, request):
        data = request.data

        #For testing, if there is a test key in the request data, return the data
        if 'test' in data:
            return Response(data, status=status.HTTP_200_OK)
        
        # Initialize the configuration
        factory = Factory()
        fitness_manager = self.configure_fitness_manager(data)
        selection_manager = self.configure_selection_manager(data)
        crossover_manager = self.configure_crossover_manager(data)
        mutation_manager = self.configure_mutation_manager(data)
        repair_manager = self.configure_repair_manager(data)
        elitism = ElitismSelection()
        elitism_size = data.get('elitism_size', 2)

        # Initialize the algorithm
        if data['algorithm']['genetic_algorithm']:
            algorithm = GeneticAlgorithm()
            algorithm.configure(factory=factory, 
                                fitness_manager=fitness_manager, 
                                selection_manager=selection_manager, 
                                crossover_manager=crossover_manager, 
                                mutation_manager=mutation_manager, 
                                repair_manager=repair_manager, 
                                elitism_selection=elitism,
                                elitism_size= elitism_size)
            
        elif data['algorithm']['genetic_local_search']:
            # Configure the local search
            neighborhood = self.configure_neighborhood(data)
            local_search = self.configure_local_search(data, fitness_manager, neighborhood)
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
            
        # Run the algorithm
        try:
            best_chromosome: Chromosome = algorithm.run(max_iteration=data.get('max_iteration', 500),
                                                        population_size=data.get('population_size', 25))
            return Response({
                # "best_chromosome": best_chromosome.to_json(),
                "best_fitness": best_chromosome.fitness,
                "time_elapsed": algorithm.log['time_elapsed'],
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
