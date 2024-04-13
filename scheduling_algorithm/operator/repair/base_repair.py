#Repairs Class
from typing import List
from scheduling_algorithm.structure import Chromosome

class BaseRepair:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Repair(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        raise NotImplementedError("Repair function not implemented")
    
class DynamicRepair(BaseRepair):
    def __init__(self, name, repair_function):
        super().__init__(name)
        self.repair_function = repair_function
    
    def __call__(self, chromosome: Chromosome):
        return self.repair_function(chromosome)
    
class RepairManager:
    '''Class to manage multiple repair functions.'''
    def __init__(self, repair_functions: List[BaseRepair]):
        self.repair_functions = repair_functions
    
    def __str__(self):
        return f"RepairManager(repair_functions={self.repair_functions})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, chromosome: Chromosome):
        for repair_function in self.repair_functions:
            chromosome = repair_function(chromosome)
        return chromosome
    
    def configure(self, repair_functions: List[BaseRepair]):
        self.repair_functions = repair_functions

