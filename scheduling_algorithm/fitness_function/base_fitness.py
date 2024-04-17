#Base Fitness Class
from scheduling_algorithm.structure import Chromosome


class BaseFitness:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Fitness(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        raise NotImplementedError("Fitness function not implemented")
    
    @classmethod
    def create(cls, name, config):
        '''Create fitness function from name and configuration, make sure the order of config is correct'''
        raise NotImplementedError("Create function not implemented")