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
        return sum([fitness_function(chromosome) for fitness_function in self.fitness_functions])
    
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
        return cls(fitness_functions)
    

config_schema = {
    # Fitness configuration, for reference only
    "type": "object",
    "properties": {
        "group_assignment_conflict": {
            "type": "object",
            "properties": {
                "max_threshold": {"type": "number"},
                "conflict_penalty": {"type": "number"}
            }
        },
        "assistant_distribution": {
            "type": "object",
            "properties": {
                "max_group_threshold": {"type": "number"},
                "max_shift_threshold": {"type": "number"},
                "group_penalty": {"type": "number"},
                "shift_penalty": {"type": "number"}
            }
        },
    },
    "required": ["group_assignment_conflict", "assistant_distribution"]
}