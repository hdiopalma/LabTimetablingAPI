from .repair import RepairManager
from .crossover import CrossoverManager
from .mutation import MutationManager
from .selection import SelectionManager

class OperatorManager:
    '''Class to manage multiple operators.'''
    def __init__(self, repair_manager: RepairManager, crossover_manager: CrossoverManager, mutation_manager: MutationManager, selection_manager: SelectionManager):
        self.repair_manager = repair_manager
        self.crossover_manager = crossover_manager
        self.mutation_manager = mutation_manager
        self.selection_manager = selection_manager
    
    def __str__(self):
        return f"OperatorManager(repair_manager={self.repair_manager}, crossover_manager={self.crossover_manager}, mutation_manager={self.mutation_manager}, selection_manager={self.selection_manager})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, population):
        '''Apply the operators to the population
        
        Args:
            population (Population): The population to apply the operators to
        
        Returns:
            Population: The population after applying the operators'''
        
        # Selection
        population = self.selection_manager(population)
        # Crossover
        population = self.crossover_manager(population)
        # Mutation
        population = self.mutation_manager(population)
        # Repair
        population = self.repair_manager(population)
        
        return population
    
    def configure(self, repair_manager: RepairManager, crossover_manager: CrossoverManager, mutation_manager: MutationManager, selection_manager: SelectionManager):
        '''Configure the operators
        
        Args:
            repair_manager (RepairManager): The repair manager to use
            crossover_manager (CrossoverManager): The crossover manager to use
            mutation_manager (MutationManager): The mutation manager to use
            selection_manager (SelectionManager): The selection manager to use'''
        
        self.repair_manager = repair_manager
        self.crossover_manager = crossover_manager
        self.mutation_manager = mutation_manager
        self.selection_manager = selection_manager
        return self

    @classmethod
    def create(cls, config):
        repair_manager = RepairManager.create(config.get("repair"))
        crossover_manager = CrossoverManager.create(config.get("crossover"))
        mutation_manager = MutationManager.create(config.get("mutation"))
        selection_manager = SelectionManager.create(config.get("selection"))
        instance = cls(repair_manager, crossover_manager, mutation_manager, selection_manager)
        return instance