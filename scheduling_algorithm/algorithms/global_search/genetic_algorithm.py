#Genetic Algorithm Class

from scheduling_algorithm.factory import Factory

#Structure
from scheduling_algorithm.structure import Chromosome, Population

#Fitness
from scheduling_algorithm.fitness_function import FitnessManager, GroupAssignmentConflictFitness, AssistantDistributionFitness

#operator
from scheduling_algorithm.operator.selection import SelectionManager, RouletteWheelSelection, TournamentSelection, ElitismSelection
from scheduling_algorithm.operator.crossover import CrossoverManager, SinglePointCrossover, TwoPointCrossover, UniformCrossover
from scheduling_algorithm.operator.mutation import MutationManager, SwapMutation, ShiftMutation, RandomMutation
from scheduling_algorithm.operator.repair import RepairManager, TimeSlotRepair

import time


class GeneticAlgorithm:

    def __init__(self):

        self.population_size = 25
        self.iteration = 100

        self.factory = Factory()
        self.fitness_manager = FitnessManager(
            [GroupAssignmentConflictFitness(),
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

    def _init_population(self, population_size):
        return self.factory.generate_population(population_size,
                                                self.fitness_manager)

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

    def __evolve(self, population: Population):
        parent1 = self.__selection(population).copy()
        parent2 = self.__selection(population).copy()

        # Crossover
        child1, child2 = self.__crossover(
            parent1, parent2
        )  # Crossover is done using deep copy, so we need to assign it back to the variable since it not modify the original chromosome

        # Mutation
        self.__mutation(
            child1
        )  # Mutation is done in place, so we don't need to assign it back to the variable
        self.__mutation(child2)

        #Repair
        self.__repair(
            child1
        )  # Repair is done in place, so we don't need to assign it back to the variable
        self.__repair(child2)

        return child1, child2

    def _evolve_population(self, population: Population):
        elitism = self.__elitism(population).copy()
        children = []

        while len(children) < len(population) - self.elitism_size:
            child1, child2 = self.__evolve(population)
            children.append(child1)
            children.append(child2)

        return Population(children, population.fitness_manager), elitism

    def run(self, *args, **kwargs):
        max_iteration = args[0] if len(args) > 0 else kwargs.get(
            'max_iteration', self.iteration)
        population_size = args[1] if len(args) > 1 else kwargs.get(
            'population_size', self.population_size)
        time_start = time.time()
        population = self._init_population(population_size)
        population.calculate_fitness()
        population = Population(
            sorted(population, key=lambda chromosome: chromosome.fitness),
            population.fitness_manager)

        for i in range(max_iteration):
            population, elitism = self._evolve_population(population)
            population.add_chromosome(elitism)
            population.calculate_fitness()

            # Sort the population based on fitness
            population = Population(
                sorted(population, key=lambda chromosome: chromosome.fitness),
                population.fitness_manager)
            if population[0].fitness == 0:
                break
        time_end = time.time()
        self.log['time_elapsed'] = (time_end - time_start)
        self.log['best_chromosome'] = population[0]
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
        print("Creating Genetic Algorithm Object from Configuration File")
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
        cls.population_size = config['population_size']
        cls.iteration = config['max_iteration']
        
        return cls().configure(factory, fitness_manager, selection_manager,
                               crossover_manager, mutation_manager,
                               repair_manager, elitism_selection, elitism_size)


#config schema for reference

algorithm_properties = {
    "type":
    "object",
    "properties": {
        "max_iteration": {
            "type": "number"
        },
        "population_size": {
            "type": "number"
        },
        "elitism_size": {
            "type": "number"
        },
        "fitness": {
            "type": "object",
            "properties": {
                "group_assignment_conflict": {
                    "type": "object",
                    "properties": {
                        "max_threshold": {
                            "type": "number"
                        },
                        "conflict_penalty": {
                            "type": "number"
                        }
                    }
                },
                "assistant_distribution": {
                    "type": "object",
                    "properties": {
                        "max_group_threshold": {
                            "type": "number"
                        },
                        "max_shift_threshold": {
                            "type": "number"
                        },
                        "group_penalty": {
                            "type": "number"
                        },
                        "shift_penalty": {
                            "type": "number"
                        }
                    }
                }
            },
            "required":
            ["group_assignment_conflict", "assistant_distribution"]
        },
        "operator": {
            "type": "object",
            "properties": {
                "selection": {
                    "type": "object",
                    "properties": {
                        "roulette_wheel": {
                            "type": "boolean"
                        },
                        "tournament": {
                            "type": "boolean"
                        },
                        "elitism": {
                            "type": "boolean"
                        },
                        "tournament_size": {
                            "type": "number"
                        }
                    },
                    "required": ["roulette_wheel", "tournament", "elitism"]
                },
                "crossover": {
                    "type": "object",
                    "properties": {
                        "single_point": {
                            "type": "boolean"
                        },
                        "two_point": {
                            "type": "boolean"
                        },
                        "uniform": {
                            "type": "boolean"
                        },
                        "crossover_probability": {
                            "type": "number"
                        },
                        "uniform_probability": {
                            "type": "number"
                        }
                    },
                    "required": ["single_point", "two_point", "uniform"]
                },
                "mutation": {
                    "type": "object",
                    "properties": {
                        "swap": {
                            "type": "boolean"
                        },
                        "shift": {
                            "type": "boolean"
                        },
                        "random": {
                            "type": "boolean"
                        },
                        "mutation_probability": {
                            "type": "number"
                        }
                    },
                    "required": ["swap", "shift", "random"]
                },
                "repair": {
                    "type": "object",
                    "properties": {
                        "time_slot": {
                            "type": "boolean"
                        }
                    },
                    "required": ["time_slot"]
                }
            },
            "required": ["selection", "crossover", "mutation", "repair"]
        },
    },
    "required": [
        "max_iteration", "population_size", "elitism_size", "fitness",
        "operator"
    ]
}
