#path: scheduling_algorithm/algorithms/local_search/tabu_search.py

import time
from typing import List, Tuple

from scheduling_algorithm.structure.tabu_list import TabuList
from scheduling_algorithm.structure.population import Population, Chromosome

from scheduling_algorithm.algorithms.local_search.base_search import BaseSearch

from scheduling_algorithm.algorithms.neighborhood import BaseNeighborhood, RandomSwapNeighborhood

from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair

from scheduling_algorithm.fitness_function import FitnessManager, GroupAssignmentCapacityFitness, AssistantDistributionFitness


class TabuSearch(BaseSearch):

    def __init__(self):
        super().__init__("TabuSearch")
        self.tabu_list = TabuList(50)
        self.neighborhood = None
        self.repair_manager = None
        self.fitness_manager = None

        # Configurable  parameters
        self.max_iteration = 1000
        self.max_stagnation = 100

        #state
        self.best_solution = None
        self.current_solution = None
        self.iteration = 0
        self.stagnation_count = 0

    def __call__(self, chromosome: Chromosome):
        return self.run(chromosome)

    def _initialize(self, chromosome: Chromosome):
        self.current_solution = chromosome.copy()
        self.current_solution.fitness = self.fitness_manager(
            self.current_solution)
        self.best_solution = self.current_solution.copy()
        self.tabu_list.clear()
        self.iteration = 0
        self.stagnation_count = 0

    def _update_solution(self, new_solution: Chromosome, move: Tuple[int,
                                                                     int]):
        '''Update the current solution with a new solution and move'''
        self.current_solution = new_solution
        self.tabu_list.add(move)

        if new_solution.fitness < self.best_solution.fitness:
            self.best_solution = new_solution.copy()
            self.stagnation_count = 0
        else:
            self.stagnation_count += 1

    def _stopping_condition(self):
        return (self.iteration >= self.max_iteration) or \
                (self.stagnation_count >= self.max_stagnation)

    def run(self, chromosome: Chromosome):
        # Initialize the search
        self._initialize(chromosome)
        while not self._stopping_condition():
            neighbors = self.neighborhood(self.current_solution)
            best_candidate = None
            best_move = None
            best_fitness = float('inf')

            for neighbor, move in neighbors:
                self.repair_manager(neighbor)
                neighbor.fitness = self.fitness_manager(neighbor)

                if (move not in self.tabu_list) or (
                        neighbor.fitness < self.best_solution.fitness):
                    if neighbor.fitness < best_fitness:
                        best_candidate = neighbor
                        best_move = move
                        best_fitness = neighbor.fitness

            if best_candidate:
                self._update_solution(best_candidate, best_move)
            else:
                self.stagnation_count += 1

            self.iteration += 1

        return self.best_solution

    def configure(self, fitness_manager, neighborhood, tabu_size,
                  max_iteration, max_stagnation):
        
        '''Configure the tabu search with fitness manager, neighborhood, and parameters.
        args:
            fitness_manager (FitnessManager): The fitness manager to evaluate solutions.
            neighborhood (BaseNeighborhood): The neighborhood structure to generate neighbors.
            tabu_size (int): Size of the tabu list.
            max_iteration (int): Maximum number of iterations.
            max_stagnation (int): Maximum number of iterations without improvement.
        '''
        
        print("Configuring Tabu Search with parameters:")
        print(f"Tabu Size: {tabu_size}, Max Iteration: {max_iteration}, Max Stagnation: {max_stagnation}")
        
        self.fitness_manager = fitness_manager
        self.neighborhood = neighborhood
        self.tabu_list.configure(tabu_size)
        self.max_iteration = max_iteration
        self.max_stagnation = max_stagnation
        self.repair_manager = RepairManager([TimeSlotRepair()])
        return self

    @classmethod
    def create(cls, fitness_manager: FitnessManager,
               neighborhood: BaseNeighborhood, config: dict):
        '''Create the search
        
        args:
            fitness_manager (FitnessManager): The fitness manager to evaluate solutions.
            neighborhood (BaseNeighborhood): The neighborhood structure to generate neighbors.
            config (dict): Configuration dictionary containing:
                - tabu_size (int): Size of the tabu list.
                - max_iteration (int): Maximum number of iterations.
                - max_stagnation (int): Maximum number of iterations without improvement.
            
        Returns:
            '''
        try:
            instance = cls()
        except Exception as e:
            print(f"Error creating Tabu Search instance: {e}")
            raise

        instance.configure(
            fitness_manager=fitness_manager,
            neighborhood=neighborhood,
            tabu_size=config["tabu_size"],
            max_iteration=config["max_iteration"],
            max_stagnation=config["max_stagnation"],
        )
        return instance


#reference
tabu_search_properties = {
    "type": "object",
    "properties": {
        "tabu_size": {
            "type": "number"
        },
        "max_iteration": {
            "type": "number"
        },
        "max_stagnation": {
            "type": "number"
        }
        
    }
}
