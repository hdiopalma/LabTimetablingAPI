import math
import random
import time
import numpy as np
from typing import List

from scheduling_algorithm.structure import Chromosome, Population
from scheduling_algorithm.algorithms.local_search.base_search import BaseSearch
from scheduling_algorithm.algorithms.neighborhood import BaseNeighborhood
from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair
from scheduling_algorithm.fitness_function import FitnessManager

class SimulatedAnnealing(BaseSearch):
    def __init__(self):
        super().__init__("SimulatedAnnealing")
        self.neighborhood = None
        self.fitness_manager = None
        self.repair_manager = None
        
        # Hyperparameters
        self.initial_temperature = 1000.0
        self.cooling_rate = 0.95
        self.min_temperature = 1.0
        self.max_iteration = 500
        self.neighborhood_size = 50
        
        # State
        self.temperature = self.initial_temperature
        self.best_solution = None
        self.current_solution = None
        
    def __call__(self, chromosome: Chromosome):
        return self.run(chromosome)

    def run(self, chromosome: Chromosome):
        self._initialize(chromosome)
        
        for iteration in range(self.max_iteration):
            if self.temperature < self.min_temperature:
                break
                
            neighbor = self._generate_neighbor()
            if self._accept_solution(neighbor):
                self.current_solution = neighbor
                
            self._update_best()
            self._cool_down()
            
        return self.best_solution

    def _initialize(self, initial_solution):
        self.current_solution = initial_solution.copy()
        self.best_solution = initial_solution.copy()
        self.current_solution.fitness = self.fitness_manager(self.current_solution)
        self.temperature = self.initial_temperature

    def _generate_neighbor(self):
        neighbors = self.neighborhood(self.current_solution)

        for neighbor in neighbors:
            # Validasi constraint
            if not self._is_valid(neighbor):
                self.repair_manager(neighbor)
            neighbor.fitness = self.fitness_manager(neighbor)

        return min(neighbors, key=lambda x: x.fitness)
    
    def _is_valid(self, chromosome: Chromosome):
        # Check unique chapter per group
        groups = chromosome["group"]
        chapters = chromosome["chapter"]
        for group in np.unique(groups):
            group_chapters = chapters[groups == group]
            if len(np.unique(group_chapters)) != len(group_chapters):
                return False
        return True

    def _accept_solution(self, neighbor):
        if neighbor.fitness < self.current_solution.fitness:
            return True
            
        probability = math.exp(-(neighbor.fitness - self.current_solution.fitness) / self.temperature)
        return random.random() < probability

    def _update_best(self):
        if self.current_solution.fitness < self.best_solution.fitness:
            self.best_solution = self.current_solution.copy()

    def _cool_down(self):
        self.temperature *= self.cooling_rate

    def configure(self, 
                 fitness_manager: FitnessManager,
                 neighborhood: BaseNeighborhood,
                 initial_temperature: float,
                 cooling_rate: float,
                 max_iteration: int,
                 neighborhood_size: int = 50):
        
        self.fitness_manager = fitness_manager
        self.neighborhood = neighborhood
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.max_iteration = max_iteration
        self.neighborhood_size = neighborhood_size
        self.repair_manager = RepairManager([TimeSlotRepair()])
        return self

    @classmethod
    def create(cls, fitness_manager: FitnessManager, neighborhood: BaseNeighborhood, config: dict):
        instance = cls()
        return instance.configure(
            fitness_manager=fitness_manager,
            neighborhood=neighborhood,
            initial_temperature=config["initial_temperature"],
            cooling_rate=config["cooling_rate"],
            max_iteration=config["max_iteration"],
            neighborhood_size=config.get("neighborhood_size", 50)
        )