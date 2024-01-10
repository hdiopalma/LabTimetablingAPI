#Fitness Manager

from typing import List
from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

class FitnessManager:
    '''FitnessManager is a class that manages all fitness functions and their respective fitness values'''
    def __init__(self, fitness_functions: List[BaseFitness]):
        self.fitness_functions = fitness_functions
    
    def __str__(self):
        return f"FitnessManager(fitness_functions={self.fitness_functions})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome) -> int:
        '''Return the total fitness value of the chromosome'''
        return sum([fitness_function(chromosome) for fitness_function in self.fitness_functions])
    
    def configure(self, fitness_functions: List[BaseFitness]):
        """Configure the fitness manager
        Args:
            fitness_functions (List[BaseFitness]): List of fitness functions"""
        
        self.fitness_functions = fitness_functions

    def grouped_fitness(self, chromosome: Chromosome):
        """Return a dictionary of fitness functions and their respective fitness value"""
        return {fitness_function.name: fitness_function(chromosome) for fitness_function in self.fitness_functions}