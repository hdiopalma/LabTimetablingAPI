#Fitness Manager

from typing import List
from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness
from scheduling_algorithm.fitness_function.group_assignment_conflict import GroupAssignmentConflictFitness
from scheduling_algorithm.fitness_function.assistant_distribution import AssistantDistributionFitness

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
        total_fitness = 0
        for fitness_function in self.fitness_functions:
            total_fitness += fitness_function(chromosome)
        return total_fitness
    
    def configure(self, fitness_functions: List[BaseFitness]):
        """Configure the fitness manager
        Args:
            fitness_functions (List[BaseFitness]): List of fitness functions"""
        
        self.fitness_functions = fitness_functions

    def grouped_fitness(self, chromosome: Chromosome):
        """Return a dictionary of fitness functions and their respective fitness value"""
        return {fitness_function.name: fitness_function(chromosome) for fitness_function in self.fitness_functions}
    
    @classmethod
    def create(cls, config: dict):
        """Create a FitnessManager instance from configuration"""
        fitness_functions = []
        for name, config in config.items():
            if name == "group_assignment_conflict":
                fitness_functions.append(GroupAssignmentConflictFitness.create(config))
            elif name == "assistant_distribution":
                fitness_functions.append(AssistantDistributionFitness.create(config))
        if not fitness_functions:
            raise ValueError("No fitness functions found in configuration")
        print("Creating FitnessManager with fitness functions: ", fitness_functions)
        instance = cls(fitness_functions)
        return instance