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
        local_search_config = self.config.get_local_search()
        return GeneticLocalSearch.create(main_config, local_search_config)
