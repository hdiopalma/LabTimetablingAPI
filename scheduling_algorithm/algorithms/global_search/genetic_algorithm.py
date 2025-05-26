#Genetic Algorithm Class

from scheduling_algorithm.factory import Factory, WeeklyFactory

#Structure
from scheduling_algorithm.structure import Chromosome, Population

#Fitness
from scheduling_algorithm.fitness_function import FitnessManager, GroupAssignmentCapacityFitness, AssistantDistributionFitness

#operator
from scheduling_algorithm.operator.selection import SelectionManager, RouletteWheelSelection, TournamentSelection, ElitismSelection
from scheduling_algorithm.operator.crossover import CrossoverManager, SinglePointCrossover, TwoPointCrossover, UniformCrossover
from scheduling_algorithm.operator.mutation import MutationManager, SwapMutation, ShiftMutation, RandomMutation
from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair

import time


class GeneticAlgorithm:

    def __init__(self):

        self.population_size = 50
        self.iteration = 500
        self.max_stagnation = 100
        self.fitness_manager = FitnessManager(
            [GroupAssignmentCapacityFitness(),
             AssistantDistributionFitness()])
        self.selection_manager = SelectionManager([
            RouletteWheelSelection(),
            TournamentSelection(),
            ElitismSelection()
        ])
        self.crossover_manager = CrossoverManager(
            [SinglePointCrossover(),
             TwoPointCrossover(),
             UniformCrossover()])
        self.mutation_manager = MutationManager(
            [SwapMutation(), ShiftMutation(),
             RandomMutation()])
    
        self.repair_manager = RepairManager([TimeSlotRepair()])
        self.elitism_size = 2
        self.elitism_selection = ElitismSelection()

        self.initial_solution = None
        self.log = {}

    def __str__(self):
        return f"GeneticAlgorithm(factory={self.factory}, selection_manager={self.selection_manager}, crossover_manager={self.crossover_manager}, mutation_manager={self.mutation_manager}, repair_manager={self.repair_manager}, elitism_size={self.elitism_size})"

    def __repr__(self):
        return self.__str__()

    def __call__(self, max_iteration: int, population_size: int):
        self.run(max_iteration, population_size)

    def __selection(
        self, population: Population
    ):  #Private method, can only be called from the class itself, subclass can't call this method.
        return self.selection_manager(population)

    def __crossover(
        self, parent1: Chromosome, parent2: Chromosome
    ):  #Private method, can only be called from the class itself, subclass can't call this method.
        return self.crossover_manager(parent1, parent2)

    def __mutation(
        self, chromosome: Chromosome
    ):  #Private method, can only be called from the class itself, subclass can't call this method.
        return self.mutation_manager(chromosome)

    def __repair(self, chromosome: Chromosome):
        return self.repair_manager(chromosome)

    def __elitism(self, population: Population):
        self.elitism_selection.elitism_size = self.elitism_size
        return self.elitism_selection(population)

    def _evolve_population(self, population: Population):
        """Evolve population with improved elitism handling"""
        # Pilih elitism dari populasi saat ini
        elites = self.__elitism(population).copy()
        
        # Bangun offspring tanpa elitism
        offspring = []
        while len(offspring) < (self.population_size - len(elites)):
            parent1 = self.__selection(population).copy()
            parent2 = self.__selection(population).copy()
            
            child1, child2 = self.__crossover(parent1, parent2)
            self.__mutation(child1)
            self.__mutation(child2)
            self.__repair(child1)
            self.__repair(child2)
            
            offspring.extend([child1, child2])
        
        # Gabungkan elites dan offspring
        new_population = Population(offspring[:self.population_size - len(elites)], population.fitness_manager)
        new_population.add_chromosome(elites)
        return new_population
    
    #init the log
    def init_log(self):
        self.log = {
            'iteration_fitness': [],
            'time_elapsed': 0,
            'best_chromosome': None,
            'stagnation_counter': 0
        }
        return self.log

    def run(self, population: Population, *args, **kwargs):
        '''Run the genetic algorithm with the given population.
        Args:
            population (Population): The initial population.
            max_iteration (int): The maximum number of iterations.
            population_size (int): The size of the population.
        '''
        self.init_log()
        max_iteration = kwargs.get('max_iteration', self.iteration)
        population_size = kwargs.get('population_size', self.population_size)
        
        
        time_start = time.time()
        population.set_fitness_manager(self.fitness_manager)
        population.calculate_fitness()
        population.sort_best()
        
        best_chromosome = population[0].copy()
        stagnation_counter = 0
        initial_mutation_prob = self.mutation_manager.mutation_probability
        
        for iteration in range(max_iteration):
            # Evolusi populasi
            population = self._evolve_population(population)
            population.calculate_fitness()
            population.sort_best()
            
            # Update best solution
            current_best = population[0]
            if current_best.fitness < best_chromosome.fitness:
                best_chromosome = current_best.copy()
                stagnation_counter = 0
                self.mutation_manager.mutation_probability = initial_mutation_prob
            else:
                stagnation_counter += 1
            
            # Adaptive mutation
            if stagnation_counter > 15:
                self.mutation_manager.mutation_probability = min(
                    initial_mutation_prob * 2.0,  # Maksimum 2x probabilitas awal
                    0.8  # Batas atas 80%
                )
            
            # Early stopping
            if stagnation_counter > self.max_stagnation or \
                best_chromosome.fitness == 0:
                break
            
            # Logging
            self.log['iteration_fitness'].append((iteration, best_chromosome.fitness))
            if iteration % 50 == 0:
                print(f"Iteration {iteration}: Best Fitness {best_chromosome.fitness}")
        
        time_end = time.time()
        self.log.update({
            'time_elapsed': time_end - time_start,
            'best_chromosome': best_chromosome,
            'stagnation_counter': stagnation_counter
        })
        return best_chromosome

    def configure(self,
                  factory: Factory = None,
                  fitness_manager: FitnessManager = None,
                  selection_manager: SelectionManager = None,
                  crossover_manager: CrossoverManager = None,
                  mutation_manager: MutationManager = None,
                  repair_manager: RepairManager = None,
                  elitism_selection: ElitismSelection = None,
                  elitism_size: int = 1):
        '''Configure the genetic algorithm, use None to use the default value.
        '''
        #self.population_size = self.population_size if population_size is None else population_size
        self.elitism_size = self.elitism_size if elitism_size is None else elitism_size
        self.elitism_selection = self.elitism_selection if elitism_selection is None else elitism_selection
        self.factory = factory if factory is not None else self.factory
        self.fitness_manager = fitness_manager if fitness_manager is not None else self.fitness_manager
        self.selection_manager = selection_manager if selection_manager is not None else self.selection_manager
        self.crossover_manager = crossover_manager if crossover_manager is not None else self.crossover_manager
        self.mutation_manager = mutation_manager if mutation_manager is not None else self.mutation_manager
        self.repair_manager = repair_manager if repair_manager is not None else self.repair_manager
        return self

    @classmethod
    def create(cls, config: dict):
        '''Create a genetic algorithm object from the configuration file.
        '''
        # factory = Factory.create(config)
        factory = Factory()
        fitness_manager = FitnessManager.create(config['fitness'])
        selection_manager = SelectionManager.create(
            config['operator']['selection'])
        crossover_manager = CrossoverManager.create(
            config['operator']['crossover'])
        mutation_manager = MutationManager.create(
            config['operator']['mutation'])
        repair_manager = RepairManager.create(config['operator']['repair'])
        elitism_selection = ElitismSelection()
        elitism_size = config['elitism_size']
        
        algorithm_instance = cls()
        algorithm_instance.population_size = config['population_size']
        algorithm_instance.iteration = config['max_iteration']
        algorithm_instance.max_stagnation = config['max_stagnation']

        print("Creating Genetic Algorithm Object from Configuration File")
        print("Population Size: ", config['population_size'])
        print("Max Iteration: ", config['max_iteration'])
        print("Max Stagnation: ", config['max_stagnation'])

        algorithm_instance.configure(factory, fitness_manager,
                                     selection_manager, crossover_manager,
                                     mutation_manager, repair_manager,
                                     elitism_selection, elitism_size)
        return algorithm_instance
