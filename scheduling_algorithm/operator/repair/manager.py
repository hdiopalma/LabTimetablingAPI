
from typing import List
from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.operator.repair.base_repair import BaseRepair
from scheduling_algorithm.operator.repair.time_slot_repair import TimeSlotRepair

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

    @classmethod
    def create(cls, config: dict):
        """Create a RepairManager from a configuration dictionary

        Args:
            config (dict): Configuration dictionary

        Raises:
            ValueError: If no repair functions are enabled

        Returns:
            RepairManager: A RepairManager instance configured with the given configuration
        """
        repair_functions = []
        if config.get("time_slot"):
            repair_functions.append(TimeSlotRepair())
        if not repair_functions:
            raise ValueError("At least one repair function must be enabled")
        return RepairManager(repair_functions)
    
#config_schema
config_schema = {
    "type": "object",
    "properties": {
        "time_slot": {"type": "boolean"}
    },
    "required": ["time_slot"]
}

