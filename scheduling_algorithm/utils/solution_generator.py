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
from ..algorithms import (
    GeneticAlgorithm,
    GeneticLocalSearch
)
from ..algorithms.local_search import (
    TabuSearch,
    SimulatedAnnealing
)

from ..factory import Factory

#Fitness function
from ..fitness_function import (
    FitnessManager,
    AssistantDistributionFitness,
    GroupAssignmentConflictFitness
)

#operator

from ..operator.manager import OperatorManager

from ..operator.selection import (
    SelectionManager,
    RouletteWheelSelection,
    TournamentSelection,
    ElitismSelection
)
from ..operator.crossover import (
    CrossoverManager, 
    SinglePointCrossover, 
    TwoPointCrossover, 
    UniformCrossover
)
from ..operator.mutation import (
    MutationManager, 
    SwapMutation, 
    ShiftMutation, 
    RandomMutation

)
from ..operator.repair import (
    RepairManager, 
    TimeSlotRepair
)

#Neighborhood for local search
from ..algorithms.neighborhood import RandomSwapNeighborhood

#Tabu list
from ..structure import Chromosome, TabuList

#Json schema for configuration, used for validation and default value

from ..config_schema import ScheduleConfiguration

class SolutionGenerator:
    def __init__(self, data):
        self.config = ScheduleConfiguration.from_data(data)
        
    def configure_algorithm(self):
        algorithm = self.config.get_algorithm()
        if algorithm == "genetic":
            return self.configure_genetic_algorithm()
        elif algorithm == "genetic_local_search":
            return self.configure_genetic_local_search_algorithm()
        else:
            raise ValueError(f"Invalid algorithm: {algorithm}")
        
    def init_config(self):
        operator_config = self.config.get_operator_config()
        operator_manager = OperatorManager.create(operator_config)

        factory = Factory()
        
        fitness = FitnessManager.create(self.config.get_fitness_config())
        selection = operator_manager.selection_manager
        crossover = operator_manager.crossover_manager
        mutation = operator_manager.mutation_manager
        repair = operator_manager.repair_manager

        elitism = ElitismSelection()
        elitism_size = self.config.get_elitism_size()

        return fitness, selection, crossover, mutation, repair, factory, elitism, elitism_size
        
    def configure_genetic_algorithm(self):
        fitness, selection, crossover, mutation, repair, factory, elitism, elitism_size = self.init_config()
        
        return GeneticAlgorithm.configure(factory, fitness, selection, crossover, mutation, repair, elitism, elitism_size)
    
    def configure_genetic_local_search_algorithm(self):
        fitness, selection, crossover, mutation, repair, factory, elitism, elitism_size = self.init_config()
        neighborhood = self.configure_neighborhood()
        local_search_algorithm = self.configure_local_search_algorithm(fitness, neighborhood)

        return GeneticLocalSearch.configure(factory, fitness, selection, crossover, mutation, repair, elitism, elitism_size, local_search_algorithm)

    def configure_neighborhood(self):
        neighborhood_config = self.config.get_neighborhood_config()
        neighborhood = RandomSwapNeighborhood(neighborhood_config["neighborhood_size"])
        return neighborhood
    
    def configure_local_search_algorithm(self, fitness, neighborhood):
        local_search_config = self.config.get_local_search()
        local_search_algorithm = local_search_config["algorithm"]

        if local_search_algorithm == "tabu_search":
            return self.configure_tabu_search(fitness, neighborhood)
        elif local_search_algorithm == "simulated_annealing":
            return self.configure_simulated_annealing(fitness, neighborhood)
        else:
            raise ValueError(f"Invalid local search algorithm: {local_search_algorithm}")
        
    def configure_tabu_search(self, fitness, neighborhood):
        local_search_config = self.config.get_tabu_search_config()

        tabu_list = TabuList(local_search_config["tabu_list_size"])
        max_iteration = local_search_config["max_iteration"]
        max_time = local_search_config["max_time"]
        max_iteration_without_improvement = local_search_config["max_iteration_without_improvement"]
        max_time_without_improvement = local_search_config["max_time_without_improvement"]

        return TabuSearch(fitness, neighborhood, tabu_list, max_iteration, max_time, max_iteration_without_improvement, max_time_without_improvement)
    
    def configure_simulated_annealing(self, fitness, neighborhood):
        local_search_config = self.config.get_simulated_annealing_config()

        initial_temperature = local_search_config["initial_temperature"]
        cooling_rate = local_search_config["cooling_rate"]
        max_iteration = local_search_config["max_iteration"]
        max_time = local_search_config["max_time"]

        return SimulatedAnnealing(fitness, neighborhood, initial_temperature, cooling_rate, max_iteration, max_time)
