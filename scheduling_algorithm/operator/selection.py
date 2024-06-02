#Selection Class

import random
from typing import List
from scheduling_algorithm.structure import Population, Chromosome

class BaseSelection:
    def __init__(self, name, probability_weight=1):
        self.name = name
        self.probability_weight = probability_weight # It is used to determine the probability of the selection function being called if more than one selection function is used.
    
    def __str__(self):
        return f"Selection(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, population: Population):
        raise NotImplementedError("Selection function not implemented")
    
    # @classmethod
    # def create(cls, name, config):
    #     '''Create selection function from name and configuration, make sure the order of config is correct'''
    #     if name == "RouletteWheelSelection":
    #         return RouletteWheelSelection()
    #     elif name == "TournamentSelection":
    #         return TournamentSelection.create(config)
    #     elif name == "ElitismSelection":
    #         return ElitismSelection.create(config)
    #     else:
    #         raise ValueError(f"Invalid selection function: {name}")
        
    
class RouletteWheelSelection(BaseSelection):
    def __init__(self):
        super().__init__("RouletteWheelSelection")
    
    def __call__(self, population: Population):
        # Calculate the total fitness
        total_fitness = sum([chromosome.fitness for chromosome in population])
        probabilities = [ 1 - (chromosome.fitness / total_fitness) for chromosome in population] # Inverse the fitness value, so the smaller fitness value has higher probability
        # probabilities = [chromosome.fitness / total_fitness for chromosome in population]
        return random.choices(population, weights=probabilities)[0] # random.choices return a list, so we need to get the first element
    
    @classmethod
    def create(cls, config):
        return cls()
    
class TournamentSelection(BaseSelection):
    def __init__(self):
        super().__init__("TournamentSelection")
        self.tournament_size = 2
    
    def __call__(self, population: Population):
        # Select a random chromosome
        chromosome = random.choice(population)
        # Select a random chromosome from the tournament size
        for i in range(self.tournament_size - 1):
            chromosome2 = random.choice(population)
            if chromosome2.fitness < chromosome.fitness:
                chromosome = chromosome2 # Select the chromosome with the lowest fitness

        return chromosome
    
    def configure(self, tournament_size):
        self.tournament_size = tournament_size

    @classmethod
    def create(cls, config):
        instance = cls()
        instance.tournament_size = config["tournament_size"]
        return instance

class ElitismSelection(BaseSelection):
    def __init__(self):
        super().__init__("ElitismSelection")
        self.elitism_size = 1
    
    def __call__(self, population: Population):
        # Sort the population based on fitness
        population = sorted(population, key=lambda chromosome: chromosome.fitness)
        # Select the best chromosome

        if self.elitism_size == 1:
            return population[0]
        
        return population[:self.elitism_size]
    
    def configure(self, elitism_size):
        self.elitism_size = elitism_size

    @classmethod
    def create(cls, config):
        instance = cls()
        instance.elitism_size = config["elitism_size"]
        return instance

class DynamicSelection(BaseSelection):
    def __init__(self, name, selection_function):
        super().__init__(name)
        self.selection_function = selection_function
    
    def __call__(self, population: Population):
        return self.selection_function(population)
    
class SelectionManager:
    '''Class to manage multiple selection functions.'''
    def __init__(self, selection_functions: List[BaseSelection]):
        self.selection_functions = selection_functions
        self.selection_probability = 0.1
    
    def __str__(self):
        return f"SelectionManager(selection_functions={self.selection_functions})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, population: Population) -> Chromosome:
        #random based on probability weight
        if random.random() < self.selection_probability:
            selection_function = self.get_random_selection()
            return selection_function(population)
        return population.get_random_chromosome()
    
    def get_random_selection(self):
        return random.choices(self.selection_functions, weights=[selection.probability_weight for selection in self.selection_functions])[0]
    
    def configure(self, selection_functions: List[BaseSelection]):
        self.selection_functions = selection_functions

    @classmethod
    def create(cls, config):
        selection_functions = []
        if config["roulette_wheel"]:
            selection_functions.append(RouletteWheelSelection.create(config))
        if config["tournament"]:
            selection_functions.append(TournamentSelection.create(config))
        if config["elitism"]:
            config["elitism_size"] = 1
            elitism = ElitismSelection.create(config)
            print("Elitism: ", elitism)
            selection_functions.append(elitism)
        if not selection_functions:
            raise ValueError("At least one selection function must be enabled")
        print("Configured selection functions: ", selection_functions)
        instance = cls(selection_functions)
        return instance