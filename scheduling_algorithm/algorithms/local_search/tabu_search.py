#path: scheduling_algorithm/algorithms/local_search/tabu_search.py

import time
from typing import List

from scheduling_algorithm.structure.tabu_list import TabuList, Chromosome
from scheduling_algorithm.structure.population import Population

from scheduling_algorithm.algorithms.local_search.base_search import BaseSearch

from scheduling_algorithm.algorithms.neighborhood import BaseNeighborhood, RandomSwapNeighborhood

from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair

from scheduling_algorithm.fitness_function import FitnessManager, GroupAssignmentCapacityFitness, AssistantDistributionFitness

class TabuSearch(BaseSearch):
    def __init__(self):
        super().__init__("TabuSearch")
        self.tabu_list = TabuList(50)
        self.neighborhood = RandomSwapNeighborhood()
        self.max_iteration = 1000
        self.max_time = 60
        self.max_iteration_without_improvement = 100
        self.max_time_without_improvement = 5
        self.iteration = 0
        self.time = 0
        self.iteration_without_improvement = 0
        self.time_without_improvement = 0
        self.best_chromosome = None
        self.best_fitness = None
        
        self.log = None
        self.log_detail = None

        self.debug = False

        self.repair_manager = RepairManager([TimeSlotRepair()])
        self.fitness_manager = FitnessManager([GroupAssignmentCapacityFitness(), AssistantDistributionFitness()])

    def __call__(self, chromosome: Chromosome):
        return self.run(chromosome)
    
    def run(self, chromosome: Chromosome):
        if self.debug:
            #Print the initial chromosome and configuration
            print("Search: ", self.name)
            print("Initial fitness: ", self.fitness_manager(chromosome))
            print("Neighborhood: ", self.neighborhood)
            print("Initial tabu list max size: ", self.tabu_list.max_size)
            print("Max iteration: ", self.max_iteration)
            print("Max time: ", self.max_time)
            print("Max iteration without improvement: ", self.max_iteration_without_improvement)
            print("Max time without improvement: ", self.max_time_without_improvement)
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
        self.iteration_without_improvement = 0
        self.time_without_improvement = 0
        # Start the search
        start = time.time()
        while self.iteration < self.max_iteration and self.time < self.max_time and self.iteration_without_improvement < self.max_iteration_without_improvement and self.time_without_improvement < self.max_time_without_improvement:
            neighbors = Population(self.get_neighbors(self.best_chromosome), self.fitness_manager)
             # Calculate the fitness of the neighbors
            neighbors.calculate_fitness()
            # Select the best neighbor
            best_neighbor = self.select_best_neighbor(neighbors.chromosomes)
            # Check if the best neighbor is better than the current best chromosome
            if best_neighbor.fitness < self.best_fitness:
                self.best_chromosome = best_neighbor.copy()
                self.best_fitness = best_neighbor.fitness
                self.iteration_without_improvement = 0
                self.time_without_improvement = 0
                self.tabu_list + best_neighbor
            else:
                self.iteration_without_improvement += 1
                self.time_without_improvement = time.time() - start - self.time
            self.iteration += 1
            self.time = time.time() - start
        return self.best_chromosome
    
    def calculate_fitness(self, neighbors: List[Chromosome]):
        '''Calculate the fitness of the neighbors'''
        for neighbor in neighbors:
            self.repair_manager(neighbor)
            neighbor.fitness = self.fitness_manager(neighbor)

    def get_neighbors(self, chromosome: Chromosome):
        '''Get the neighbors of the chromosome'''
        return self.neighborhood(chromosome)
    
    def select_best_neighbor(self, neighbors: List[Chromosome]):
        '''Select the best neighbor from the neighbors'''
        best_neighbor = neighbors[0]
        for neighbor in neighbors:
            if neighbor not in self.tabu_list and neighbor.fitness < best_neighbor.fitness:
                best_neighbor = neighbor
        return best_neighbor
    
    def configure(self, fitness_manager: FitnessManager, tabu_list: TabuList, neighborhood: BaseNeighborhood, max_iteration: int, max_time: int, max_iteration_without_improvement: int, max_time_without_improvement: int):
        '''Configure the search
        
        args:
            fitness_manager: FitnessManager
            tabu_list: TabuList
            neighborhood: BaseNeighborhood
            max_iteration: int
            max_time: int
            max_iteration_without_improvement: int
            max_time_without_improvement: int'''
        
        self.fitness_manager = fitness_manager or self.fitness_manager
        self.tabu_list = tabu_list or self.tabu_list
        self.neighborhood = neighborhood or self.neighborhood
        self.max_iteration = max_iteration or self.max_iteration
        self.max_time = max_time or self.max_time
        self.max_iteration_without_improvement = max_iteration_without_improvement or self.max_iteration_without_improvement
        self.max_time_without_improvement = max_time_without_improvement or self.max_time_without_improvement
        return self
    
    @classmethod
    def create(cls, fitness_manager: FitnessManager, neighborhood: BaseNeighborhood, config: dict):
        '''Create the search
        
        args:
            fitness_config: dict
            tabu_search_config: dict
            neighborhood: BaseNeighborhood'''
        
        tabu_list = TabuList(config["tabu_list_size"])
        max_iteration = config["max_iteration"]
        max_time = config["max_time"]
        max_iteration_without_improvement = config["max_iteration_without_improvement"]
        max_time_without_improvement = config["max_time_without_improvement"]
        instance = cls().configure(fitness_manager, tabu_list, neighborhood, max_iteration, max_time, max_iteration_without_improvement, max_time_without_improvement)
        return instance
        
#reference
tabu_search_properties = {
    "type": "object",
    "properties": {
        "tabu_list_size": {"type": "number"},
        "max_iteration": {"type": "number"},
        "max_time": {"type": "number"},
        "max_iteration_without_improvement": {"type": "number"},
        "max_time_without_improvement": {"type": "number"}
    }
}