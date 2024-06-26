#Genetic Algorithm Class
from scheduling_algorithm.algorithms.global_search.genetic_algorithm import GeneticAlgorithm
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


class SteadyStateGeneticAlgorithm(GeneticAlgorithm):
    """
    Steady-state genetic algorithm is different from the generational 
    genetic algorithm in which only two chromosomes are selected to undergo 
    crossover and mutation to generate two children. Two worst chromosomes 
    will be chosen from the population to be replaced by the new children. 
    It updates the population in a piecemeal fashion rather than all at one time.

    Args:
        GeneticAlgorithm (class): Genetic Algorithm Class
    """

    def __init__(self):

        self.population_size = 25
        self.iteration = 100
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
        return f"SteadyStateGeneticAlgorithm(factory={self.factory}, selection_manager={self.selection_manager}, crossover_manager={self.crossover_manager}, mutation_manager={self.mutation_manager}, repair_manager={self.repair_manager}, elitism_size={self.elitism_size})"

    def _evolve_population(self, population: Population):
        # elitism = self.__elitism(population).copy()
        children = []

        child1, child2 = self.__evolve(population)
        children.append(child1)
        children.append(child2)
        
        population.replace_worst(children)

        return population

    def run(self, population: Population, *args, **kwargs):
        max_iteration = args[0] if len(args) > 0 else kwargs.get(
            'max_iteration', self.iteration)
        population_size = args[1] if len(args) > 1 else kwargs.get(
            'population_size', self.population_size)

        time_start = time.time()
        self.log['iteration_fitness'] = []
        population.set_fitness_manager(self.fitness_manager)
        population.calculate_fitness()
        population.sort_best()

        stagnation_counter = 0
        last_fitness = population[0].fitness
        initial_mutation_probability = self.mutation_manager.mutation_probability

        for i in range(max_iteration):
            population = self._evolve_population(population)
            population.calculate_fitness()
            population.sort_best()
            if len(population) > population_size:
                population.pop()

            # Stagnation Counter Section
            if population[0].fitness == last_fitness:
                stagnation_counter += 1
            else:
                stagnation_counter = 0
                self.mutation_manager.mutation_probability = initial_mutation_probability
            last_fitness = population[0].fitness
            if stagnation_counter > self.iteration // 2:
                print("Stagnation Counter Exceeded Half of the Iteration, Halting the Algorithm")
                break
            if stagnation_counter > 50:
                pass
            elif stagnation_counter > 15:
                self.mutation_manager.mutation_probability *= 1.25
            # End of Stagnation Counter Section
            
            print(f"Iteration: {i}, Fittest Chromosome: {self.fitness_manager(population[0])}")
            self.log['iteration_fitness'].append((i, population[0].fitness))
            if population[0].fitness == 0:
                break
            
        time_end = time.time()
        self.log['time_elapsed'] = (time_end - time_start)
        self.log['best_chromosome'] = population[0]
        print(f"Fittest Chromosome: {self.fitness_manager(population[0])}")
        return population[0]

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

        print("Creating Genetic Algorithm Object from Configuration File")
        print("Population Size: ", config['population_size'])
        print("Max Iteration: ", config['max_iteration'])

        algorithm_instance.configure(factory, fitness_manager,
                                     selection_manager, crossover_manager,
                                     mutation_manager, repair_manager,
                                     elitism_selection, elitism_size)
        return algorithm_instance
