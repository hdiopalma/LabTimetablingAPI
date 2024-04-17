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
