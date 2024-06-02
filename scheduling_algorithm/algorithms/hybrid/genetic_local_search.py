#Hybrid Algorithm Class
# Create a hybrid algorithm class that combine the genetic algorithm and tabu search, the genetic algorithm will be used to generate the initial solution and focus on the exploration, while the tabu search will be used to improve the solution and focus on the exploitation.

from scheduling_algorithm.structure import Population

from scheduling_algorithm.algorithms.global_search.genetic_algorithm import GeneticAlgorithm

from scheduling_algorithm.algorithms.local_search.manager import LocalSearchManager
from scheduling_algorithm.algorithms.local_search.tabu_search import TabuSearch
from scheduling_algorithm.algorithms.local_search.simulated_annealing import SimulatedAnnealing

from scheduling_algorithm.factory.factory import Factory

from scheduling_algorithm.fitness_function import FitnessManager
from scheduling_algorithm.operator.crossover import CrossoverManager
from scheduling_algorithm.operator.mutation import MutationManager
from scheduling_algorithm.operator.repair import RepairManager
from scheduling_algorithm.operator.selection import SelectionManager, ElitismSelection

import time

import cProfile

class GeneticLocalSearch(GeneticAlgorithm):
    def __init__(self):
        super().__init__()
        self.local_search = SimulatedAnnealing()
        self.log['local_search_improvements'] = []
    
    def __str__(self):
        return f"GeneticLocalSearch(factory={self.factory}, selection_manager={self.selection_manager}, crossover_manager={self.crossover_manager}, mutation_manager={self.mutation_manager}, repair_manager={self.repair_manager}, elitism_size={self.elitism_size}, local_search={self.local_search})"
    
    def __repr__(self):
        return self.__str__()
    
    def run(self, population: Population, *args, **kwargs):
        '''Run the hybrid algorithm.
        '''
        max_iteration = args[0] if len(args) > 0 else kwargs.get(
            'max_iteration', self.iteration)
        population_size = args[1] if len(args) > 1 else kwargs.get(
            'population_size', self.population_size)
        
        time_start = time.time()
        # Calculate the fitness of the initial population
        population.set_fitness_manager(self.fitness_manager)
        population.calculate_fitness()
        # Sort the population based on fitness
        population = Population(sorted(population, key=lambda chromosome: chromosome.fitness), population.fitness_manager)
        # Initialize the best chromosome
        best_chromosome = population[0].copy()
        # Initialize the iteration
        iteration = 0
        self.log['iteration_fitness'] = []
        # Start the hybrid algorithm
        while iteration < max_iteration and best_chromosome.fitness > 0:
            # Evolve the population, crossover and mutation happens inside this function (This is the genetic algorithm part)
            offspring, elitism = self._evolve_population(population)

            # Add the elitism back to the population
            offspring.add_chromosome(elitism)
            offspring.calculate_fitness()
            
            # Introduction of local search, for possible improvement of previous best chromosome
            # Note: Don't set the iteration or time too high, this is not the main algorithm.
            local_search_result = self.local_search(best_chromosome)
            if local_search_result.fitness < best_chromosome.fitness:
                self.log['local_search_improvements'].append((iteration, best_chromosome.fitness, local_search_result.fitness))
            offspring.add_chromosome(local_search_result)

            # Sort the population based on fitness
            population = Population(sorted(offspring, key=lambda chromosome: chromosome.fitness), population.fitness_manager)
            #remove the worst chromosome, so the population size is still the same
            if len(population) > population_size:
                population.pop()
            # Check if the best chromosome is better than the current best chromosome
            
            if population[0].fitness < best_chromosome.fitness:
                best_chromosome = population[0].copy()
            self.log['iteration_fitness'].append((iteration, best_chromosome.fitness))
            iteration += 1
            
        time_end = time.time()
        self.log['time_elapsed'] = time_end - time_start
        self.log['best_chromosome'] = best_chromosome
        print("Best Fitness: ", best_chromosome.fitness)
        return best_chromosome
    
    def configure(self, factory: Factory = None, fitness_manager: FitnessManager = None, selection_manager: SelectionManager = None, crossover_manager: CrossoverManager = None, mutation_manager: MutationManager = None, repair_manager: RepairManager = None, elitism_selection: ElitismSelection = None, elitism_size: int = 1, local_search = None):
        '''Configure the hybrid algorithm, use None to use the default value.
        '''
        self.elitism_size = elitism_size or self.elitism_size
        self.elitism_selection = elitism_selection or self.elitism_selection
        self.factory = factory or self.factory
        self.fitness_manager = fitness_manager or self.fitness_manager
        self.selection_manager = selection_manager or self.selection_manager
        self.crossover_manager = crossover_manager or self.crossover_manager
        self.mutation_manager = mutation_manager or self.mutation_manager
        self.repair_manager = repair_manager or self.repair_manager
        self.local_search = local_search or self.local_search
        return self
    
    @classmethod
    def create(cls, main_config: dict, local_search_config: dict):
        """_summary_

        Args:
            main_config (dict): The main configuration for the genetic algorithm such as max_iteration, population_size, etc.
            local_search_config (dict): The configuration for the local search algorithm such as tabu_search or simulated_annealing

        Returns:
            GeneticLocalSearch: The configured genetic local search algorithm
        """
        # factory = Factory.create(config)
        print("Creating Genetic Local Search Algorithm from configuration")
        print("Population Size: ", main_config['population_size'])
        print("Max Iteration: ", main_config['max_iteration'])
        factory = Factory()
        fitness_manager = FitnessManager.create(main_config["fitness"])
        selection_manager = SelectionManager.create(main_config["operator"]["selection"])
        crossover_manager = CrossoverManager.create(main_config["operator"]["crossover"])
        mutation_manager = MutationManager.create(main_config["operator"]["mutation"])
        repair_manager = RepairManager.create(main_config["operator"]["repair"])
        elitism_selection = ElitismSelection()
        elitism_size = main_config["elitism_size"]
        local_search = LocalSearchManager.create(local_search_config, fitness_manager)
        print("Local Search Algorithm: ", local_search)
        instance = cls().configure(factory, fitness_manager, selection_manager, crossover_manager, mutation_manager, repair_manager, elitism_selection, elitism_size, local_search)
        instance.population_size = main_config['population_size']
        instance.iteration = main_config['max_iteration']
        return instance