#Crossover Class

import random
from typing import List

from scheduling_algorithm.structure import Chromosome

class BaseCrossover:
    def __init__(self, name, probability_weight=1):
        self.name = name
        self.probability_weight = probability_weight # It is used to determine the probability of the crossover function being called if more than one crossover function is used.
    
    def __str__(self):
        return f"Crossover(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, parent1: Chromosome, parent2: Chromosome):
        raise NotImplementedError("Crossover function not implemented")
    
class SinglePointCrossover(BaseCrossover):
    def __init__(self):
        super().__init__("SinglePointCrossover")
    
    def __call__(self, parent1: Chromosome, parent2: Chromosome):
        # Randomly select a point
        point = random.randint(0, len(parent1))
        child1 = parent1 # already deepcopy in the selection part of the algorithm
        child2 = parent2
        #swap that point onwards
        child1.gene_data[point:], child2.gene_data[point:] = child2.gene_data[point:], child1.gene_data[point:]

        return child1, child2
    
class TwoPointCrossover(BaseCrossover):
    def __init__(self):
        super().__init__("TwoPointCrossover")
    
    def __call__(self, parent1: Chromosome, parent2: Chromosome):
        # Randomly select 2 points
        point1 = random.randint(0, len(parent1))
        point2 = random.randint(0, len(parent1))
        # initialize the children
        child1 = parent1
        child2 = parent2
        #swap a section of the chromosome between the 2 points
        if point1 > point2:
            point1, point2 = point2, point1
        child1.gene_data[point1:point2], child2.gene_data[point1:point2] = child2.gene_data[point1:point2], child1.gene_data[point1:point2]

        return child1, child2
    
class UniformCrossover(BaseCrossover):
    def __init__(self):
        super().__init__("UniformCrossover")
        self.uniform_probability = 0.5
    
    def __call__(self, parent1: Chromosome, parent2: Chromosome):
        # initialize the children
        child1 = parent1
        child2 = parent2
        #swap a section of the chromosome between the 2 points
        count = 0
        for i in range(len(child1)):
            if random.random() < self.uniform_probability:
                count += 1
                child1.gene_data[i], child2.gene_data[i] = child2.gene_data[i], child1.gene_data[i]
        
        return child1, child2
    
    def configure(self, uniform_probability):
        '''Configure the crossover function
        
        Args:
            uniform_probability (float): The probability of swapping a gene between the 2 parents on a particular index'''
        
        self.uniform_probability = uniform_probability

class DynamicCrossover(BaseCrossover):
    def __init__(self, name, crossover_function):
        super().__init__(name)
        self.crossover_function = crossover_function
    
    def __call__(self, parent1: Chromosome, parent2: Chromosome):
        return self.crossover_function(parent1, parent2)
    
class CrossoverManager:
    '''Class to manage multiple crossover functions.'''
    def __init__(self, crossover_functions: List[BaseCrossover]):
        self.crossover_functions = crossover_functions
        self.crossover_probability = 0.1
    
    def __str__(self):
        return f"CrossoverManager(crossover_functions={self.crossover_functions})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, parent1: Chromosome, parent2: Chromosome):
        #random based on probability weight
        if random.random() < self.crossover_probability:
            crossover_function = self.get_random_crossover()
            return crossover_function(parent1, parent2)
        return parent1, parent2
    
    def get_random_crossover(self):
        return random.choices(self.crossover_functions, weights=[crossover.probability_weight for crossover in self.crossover_functions])[0]
    
    def configure(self, crossover_probability):
        self.crossover_probability = crossover_probability
        return self
    
    @classmethod
    def create(cls, config):
        '''Create crossover manager from configuration'''
        crossover_functions = []
        if config.get("single_point", False):
            crossover_functions.append(SinglePointCrossover())
        if config.get("two_point", False):
            crossover_functions.append(TwoPointCrossover())
        if config.get("uniform", False):
            uniform_crossover = UniformCrossover()
            if "uniform_probability" in config:
                uniform_crossover.configure(config["uniform_probability"])
            crossover_functions.append(uniform_crossover)
        if not crossover_functions:
            raise ValueError("At least one crossover function must be enabled")
        print("Configuring crossover operator: ", crossover_functions)
        return CrossoverManager(crossover_functions).configure(config.get("crossover_probability", 0.1))
    
config_schema = {
    # Crossover configuration, for reference only
    "type": "object",
    "properties": {
        "single_point": {"type": "boolean"},
        "two_point": {"type": "boolean"},
        "uniform": {"type": "boolean"},
        "uniform_probability": {"type": "number"},
        "crossover_probability": {"type": "number"}
    }
}