##### Simulated Annealing

# Simulated Annealing Class

import math
import random
import time
from typing import List

from scheduling_algorithm.structure import Chromosome, Population
from scheduling_algorithm.algorithms.local_search.base_search import BaseSearch
from scheduling_algorithm.algorithms.neighborhood import RandomSwapNeighborhood, BaseNeighborhood
from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair
from scheduling_algorithm.fitness_function import FitnessManager, GroupAssignmentCapacityFitness, AssistantDistributionFitness

class SimulatedAnnealing(BaseSearch):
    def __init__(self):
        super().__init__("SimulatedAnnealing")
        self.neighborhood_algorithm = RandomSwapNeighborhood()
        self.initial_temperature = 100
        self.temperature = 100
        self.temperature_threshold = 0.1
        self.cooling_rate = 0.1
        self.max_iteration = 1000
        self.iteration_without_improvement = 0
        self.max_iteration_without_improvement = 100
        self.max_time = 60
        self.best_chromosome = None
        self.best_fitness = None
        self.iteration = 0
        self.time = 0
        self.log = None
        self.log_detail = None
        self.information = None

        self.debug = False

        self.termination_reason = None

        self.repair_manager = RepairManager([TimeSlotRepair()])
        self.fitness_manager = None

    def print_configuration(self):
        print("Search: ", self.name)
        print("Initial temperature: ", self.initial_temperature)
        print("Cooling rate: ", self.cooling_rate)
        print("Max iteration: ", self.max_iteration)
        print("Max iteration without improvement: ", self.max_iteration_without_improvement)
        print("Max time: ", self.max_time)

    def __call__(self, chromosome: Chromosome):
        return self.run(chromosome)
    
    def run(self, chromosome: Chromosome):
        if self.debug:
            #Print the initial chromosome and configuration
            print("Search: ", self.name)
            print("Initial fitness: ", self.fitness_manager(chromosome))
            print("Neighborhood: ", self.neighborhood_algorithm)
            print("Initial temperature: ", self.initial_temperature)
            print("Cooling rate: ", self.cooling_rate)
            print("Max iteration: ", self.max_iteration)
            print("Max time: ", self.max_time)
            print("--------------------------------------------------")

        # Initialize the best chromosome
        self.best_chromosome = chromosome.copy()
        self.best_fitness = chromosome.fitness
        # Initialize the log
        self.log = []
        self.log_detail = []
        # Initialize the iteration
        self.iteration = 0
        self.time = 0
        # Initialize the temperature
        self.temperature = self.initial_temperature
        # Start the search
        start = time.time()
        while self.awake():
            self.log.append({"iteration": self.iteration, "time": self.time, "fitness": self.best_fitness})
            self.log_detail.append({"iteration": self.iteration, "time": self.time, "fitness": self.best_fitness, "chromosome": self.best_chromosome})
            # Get the neighbors
            neighbors = Population(self.get_neighbors(self.best_chromosome), self.fitness_manager)
            # Calculate the fitness of the neighbors
            neighbors.calculate_fitness()
            # Select the best neighbor
            best_neighbor = self.select_best_neighbor(neighbors.chromosomes)
            # Calculate the probability of accepting the neighbor
            probability = self.calculate_probability(best_neighbor.fitness)
            if random.random() < probability:
                self.best_chromosome = best_neighbor.copy()
                self.best_fitness = best_neighbor.fitness
                self.iteration_without_improvement = 0
            else:
                self.iteration_without_improvement += 1
            # Cool down the temperature
            self.cool_down()
            self.iteration += 1
            self.time = time.time() - start

        #Check if the best chromosome is better than the initial chromosome
        if self.best_fitness > chromosome.fitness:
            self.best_chromosome = chromosome.copy()
            self.best_fitness = chromosome.fitness
        
        # Return the best chromosome
        self.information = {"iteration": self.iteration, "time": self.time, "fitness": self.best_fitness, "chromosome": self.best_chromosome, "termination_reason": self.termination_reason}
        self.repair_manager(self.best_chromosome)
        return self.best_chromosome
    
    def awake(self) -> bool:
        '''Check if the search should continue'''
        # reached_max_iteration = self.iteration >= self.max_iteration
        # reached_max_time = self.time >= self.max_time
        # reached_max_iteration_without_improvement = self.iteration_without_improvement >= self.max_iteration_without_improvement
        reached_temperature_threshold = self.temperature <= self.temperature_threshold
        reached_best_fitness = self.best_fitness == 0
        # self.termination_reason =   \
        #                         "Reached max iteration" if reached_max_iteration else \
        #                         "Reached max time" if reached_max_time else \
        #                         "Reached max iteration without improvement" if reached_max_iteration_without_improvement else \
        #                         "Reached temperature threshold" if reached_temperature_threshold else \
        #                         "Reached best fitness" if reached_best_fitness else \
        #                         None
        return (
                # not reached_max_iteration and \
                # not reached_max_time and \
                # not reached_max_iteration_without_improvement and \
                not reached_temperature_threshold
                ) and \
                not reached_best_fitness
    
    def calculate_fitness(self, neighbors: List[Chromosome]):
        '''Calculate the fitness of the neighbors'''
        
        for neighbor in neighbors:
            self.repair_manager(neighbor)
            neighbor.fitness = self.fitness_manager(neighbor)

    def get_neighbors(self, chromosome: Chromosome):
        '''Get the neighbors of the chromosome'''
        return self.neighborhood_algorithm(chromosome)
    
    def select_best_neighbor(self, neighbors: List[Chromosome]):
        '''Select the best neighbor from the neighbors'''
        best_neighbor = neighbors[0]
        for neighbor in neighbors:
            if neighbor.fitness < best_neighbor.fitness:
                best_neighbor = neighbor
        return best_neighbor
    
    def calculate_probability(self, neighbor_fitness: float):
        """Calculate the probability of accepting a worse neighbor."""
        delta_e = neighbor_fitness - self.best_fitness
        if delta_e < 0:
            return 1.0
        else:
            exponent = delta_e / self.temperature  
            return math.exp(exponent)  # Boltzmann probability
    
    def cool_down(self):
        '''Cool down the temperature'''
        # Method used: Exponential cooling
        # Example: 90 * 1 - 0.09 = 81
        # Example: 81 * 1 - 0.09 = 72.9
        self.temperature *= 1 - self.cooling_rate

    def configure(self, fitness_manager: FitnessManager = None, neighborhood: BaseNeighborhood = None, initial_temperature: float = None, cooling_rate: float = None, max_iteration: int = None, max_iteration_without_improvement: int = None, max_time: int = None):
        '''Configure the search
        
        args:
            fitness_manager: FitnessManager
            neighborhood: BaseNeighborhood
            initial_temperature: float
            cooling_rate: float
            max_iteration: int
            max_time: int'''
        
        self.fitness_manager = fitness_manager or self.fitness_manager
        self.neighborhood_algorithm = neighborhood or self.neighborhood_algorithm
        self.initial_temperature = initial_temperature or self.initial_temperature
        self.temperature = initial_temperature or self.initial_temperature
        self.cooling_rate = cooling_rate or self.cooling_rate
        self.max_iteration = max_iteration or self.max_iteration
        self.max_time = max_time or self.max_time
        self.max_iteration_without_improvement = max_iteration_without_improvement or self.max_iteration_without_improvement

        print("Configuration:")
        print("Fitness Manager: ", self.fitness_manager)
        self.print_configuration()

        return self
    
    @classmethod
    def create(cls, fitness_manager: FitnessManager, neighborhood: BaseNeighborhood, config: dict):
        '''Create the search
        
        args:
            fitness_manager: FitnessManager
            neighborhood: BaseNeighborhood
            config: dict'''
            
        fitness_manager = fitness_manager
        neighborhood = neighborhood
        initial_temperature = config["initial_temperature"]
        cooling_rate = config["cooling_rate"]
        max_iteration = config["max_iteration"]
        max_iteration_without_improvement = config["max_iteration_without_improvement"]
        max_time = config["max_time"]
        instance = cls()
        instance.configure(fitness_manager, neighborhood, initial_temperature, cooling_rate, max_iteration, max_iteration_without_improvement, max_time)
        return instance
    
    def get_log(self):
        return self.log
    
    def get_log_detail(self):
        return self.log_detail