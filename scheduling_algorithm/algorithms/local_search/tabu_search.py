import time
from typing import List

from scheduling_algorithm.structure.tabu_list import TabuList, Chromosome

from scheduling_algorithm.algorithms.local_search.base_search import BaseSearch

from scheduling_algorithm.algorithms.neighborhood import BaseNeighborhood, RandomSwapNeighborhood

from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair

from scheduling_algorithm.fitness_function import FitnessManager

class TabuSearch(BaseSearch):
    def __init__(self):
        super().__init__("TabuSearch")
        self.tabu_list = TabuList(10)
        self.neighborhood = RandomSwapNeighborhood()
        self.max_iteration = 1000
        self.max_time = 60
        self.max_iteration_without_improvement = 100
        self.max_time_without_improvement = 10
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
            #self.log.append({"iteration": self.iteration, "time": self.time, "iteration_without_improvement": self.iteration_without_improvement, "time_without_improvement": self.time_without_improvement, "fitness": self.best_fitness})
            #self.log_detail.append({"iteration": self.iteration, "time": self.time, "iteration_without_improvement": self.iteration_without_improvement, "time_without_improvement": self.time_without_improvement, "fitness": self.best_fitness, "chromosome": self.best_chromosome})
            # Get the neighbors
            neighbors = self.get_neighbors(self.best_chromosome)
            # Repair the neighbors
            # Calculate the fitness of the neighbors
            self.calculate_fitness(neighbors)
            # Select the best neighbor
            best_neighbor = self.select_best_neighbor(neighbors)
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