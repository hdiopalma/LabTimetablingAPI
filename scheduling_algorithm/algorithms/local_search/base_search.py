from scheduling_algorithm.structure import Chromosome

from scheduling_algorithm.fitness_function import FitnessManager, GroupAssignmentConflictFitness, AssistantDistributionFitness

class BaseSearch:
    def __init__(self, name):
        self.name = name
        self.fitness_manager = FitnessManager([GroupAssignmentConflictFitness(), AssistantDistributionFitness()])
    
    def __str__(self):
        return f"Search(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        raise NotImplementedError("Search function not implemented")
    
    def configure(self, fitness_manager: FitnessManager):
        raise NotImplementedError("Configure function not implemented")