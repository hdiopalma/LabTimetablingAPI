from collections import defaultdict
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

import numpy as np

#Maximize the utilization of assistants by distributing tasks evenly among them. Each assistant should be assigned to a balanced number of groups and shift to avoid overloading.
class AssistantDistributionFitness(BaseFitness):
    def __init__(self):
        super().__init__("AssistantDistributionFitness")
        self.max_group_threshold = None # Maximum number of groups that can be assigned to a single assistant
        self.max_shift_threshold = None # Maximum number of shifts that can be assigned to a single assistant
        self.group_penalty = 1 # Penalty for each group that exceeds the maximum threshold
        self.shift_penalty = 1 # Penalty for each shift that exceeds the maximum threshold

        #groups[assistant][module] = [groups]
        self._groups = self.default_middle_dict()
        #shifts[assistant][module] = [shifts]
        self._shifts = self.default_middle_dict()

    def default_inner_dict(self):
        return defaultdict(set)
    
    def default_middle_dict(self):
        return defaultdict(self.default_inner_dict)
    
    def default_outer_dict(self):
        return defaultdict(self.default_middle_dict)
    
    def __call__(self, chromosome: Chromosome):
        self._groups.clear()
        self._shifts.clear()
        for gene in chromosome:
            self._groups[gene["assistant"]][gene["module"]].add(gene["group"])
            self._shifts[gene["assistant"]][gene["module"]].add(gene["time_slot"])
        
        total_penalty = 0
        for assistant in self._groups:
            for module in self._groups[assistant]:
                groups = self._groups[assistant][module]
                shifts = self._shifts[assistant][module]
                if len(groups) > self.max_group_threshold:
                    total_penalty += (len(groups) - self.max_group_threshold) * self.group_penalty
                if len(shifts) > self.max_shift_threshold:
                    total_penalty += (len(shifts) - self.max_shift_threshold) * self.shift_penalty
        return total_penalty
    
    # def __call__(self, chromosome: Chromosome):
    #     #convert chromosome data to numpy array
    #     assistant = np.array([gene["assistant"] for gene in chromosome])
    #     module = np.array([gene["module"] for gene in chromosome])
    #     group = np.array([gene["group"] for gene in chromosome])
    #     time_slot = np.array([gene["time_slot"] for gene in chromosome])
        
    #     total_penalty = 0
        
    #     #count the number of groups and shifts assigned to each assistant
    #     for assistant_id in np.unique(assistant):
    #         for module_id in np.unique(module[assistant == assistant_id]):
    #             mask = (assistant == assistant_id) & (module == module_id)
    #             unique_groups = np.unique(group[mask])
    #             unique_shifts = np.unique(time_slot[mask])
                
    #             group_penalty = max(0, len(unique_groups) - self.max_group_threshold) * self.group_penalty
    #             shift_penalty = max(0, len(unique_shifts) - self.max_shift_threshold) * self.shift_penalty
                
    #             total_penalty += group_penalty + shift_penalty
        
    #     return total_penalty
            
        
    
    def get_groups(self):
        return self._groups
    
    def get_shifts(self):
        return self._shifts
    
    def configure(self, max_group_threshold, max_shift_threshold, group_penalty, shift_penalty):
        """Configure the fitness function
        Args:
            max_group_threshold (int): Maximum number of groups that can be assigned to a single assistant
            max_shift_threshold (int): Maximum number of shifts that can be assigned to a single assistant
            group_penalty (int): Penalty for each group that exceeds the maximum threshold
            shift_penalty (int): Penalty for each shift that exceeds the maximum threshold"""
        self.max_group_threshold = max_group_threshold
        self.max_shift_threshold = max_shift_threshold
        self.group_penalty = group_penalty
        self.shift_penalty = shift_penalty
        return self
    
    @classmethod
    def create(cls, config):
        """Create AssistantDistributionFitness instance from configuration
        Args:
            config (dict): Configuration for the fitness function
            config = {
                "max_group_threshold": 15,
                "max_shift_threshold": 50,
                "group_penalty": 1,
                "shift_penalty": 1
            }
        """
        instance = cls().configure(**config)
        return instance
