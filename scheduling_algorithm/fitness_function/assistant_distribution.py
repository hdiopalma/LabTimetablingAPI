from collections import defaultdict
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

import numpy as np

#Maximize the utilization of assistants by distributing tasks evenly among them. Each assistant should be assigned to a balanced number of groups and shift to avoid overloading.
class AssistantDistributionFitness(BaseFitness):
    def __init__(self):
        super().__init__("AssistantDistributionFitness")
        self.max_group_threshold = None
        self.max_shift_threshold = None
        self.group_penalty = 1
        self.shift_penalty = 1
        
    def __str__(self):
        message = f"Fitness(name={self.name}, max_group_threshold={self.max_group_threshold}, max_shift_threshold={self.max_shift_threshold}, group_penalty={self.group_penalty}, shift_penalty={self.shift_penalty})"
        return message

    def calculate_penalty(self, groups, shifts):
        total_penalty = 0
        for assistant in groups:
            for module in groups[assistant]:
                group_count = len(groups[assistant][module])
                shift_count = len(shifts[assistant][module])
                if group_count > self.max_group_threshold:
                    total_penalty += (group_count - self.max_group_threshold) * self.group_penalty
                if shift_count > self.max_shift_threshold:
                    total_penalty += (shift_count - self.max_shift_threshold) * self.shift_penalty
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
