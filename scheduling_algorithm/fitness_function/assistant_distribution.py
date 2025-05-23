#path: scheduling_algorithm/fitness_function/assistant_distribution.py

from collections import Counter, defaultdict
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

import numpy as np

#Maximize the utilization of assistants by distributing tasks evenly among them. Each assistant should be assigned to a balanced number of groups and shift to avoid overloading.
class AssistantDistributionFitness(BaseFitness):
    def __init__(self):
        """Fitness function to penalize conflicts in assistant distribution. (e.g. an assistant is assigned to too many groups or shifts)
        (Jumlah maksimal kelompok dan shift yang diambil oleh assistent dalam satu periode)
        """
        super().__init__("AssistantDistributionFitness")
        self.max_group_threshold = None
        self.max_shift_threshold = None
        self.group_penalty = 1
        self.shift_penalty = 1
        
    def __str__(self):
        message = f"Fitness(name={self.name}, max_group_threshold={self.max_group_threshold}, max_shift_threshold={self.max_shift_threshold}, group_penalty={self.group_penalty}, shift_penalty={self.shift_penalty})"
        return message

    def calculate_penalty(self, modules, assistants, groups, timeslot_date, timeslot_shift):
    # Convert to NumPy arrays for vectorized operations
        modules = np.asarray(modules)
        groups = np.asarray(groups)
        timeslot_date = np.asarray(timeslot_date)
        timeslot_shift = np.asarray(timeslot_shift)
        assistants = np.asarray(assistants)
    
        # Precompute unique identifiers for groups and shifts
        group_pairs = np.core.records.fromarrays([modules, groups], names='module,group')
        shift_triplets = np.core.records.fromarrays([modules, timeslot_date, timeslot_shift], names='module,date,shift')
    
        # Get unique assistants and prepare masks
        unique_assistants, assistant_indices = np.unique(assistants, return_inverse=True)
        n_assistants = len(unique_assistants)
    
        # Vectorized counting of unique entries per assistant
        group_counts = np.empty(n_assistants, dtype=int)
        shift_counts = np.empty(n_assistants, dtype=int)
    
        for i in range(n_assistants):
            mask = (assistant_indices == i)
            group_counts[i] = np.unique(group_pairs[mask]).size
            shift_counts[i] = np.unique(shift_triplets[mask]).size
    
        # Calculate penalties
        group_over = np.maximum(group_counts - self.max_group_threshold, 0)
        shift_over = np.maximum(shift_counts - self.max_shift_threshold, 0)
        return np.sum(group_over * self.group_penalty + shift_over * self.shift_penalty)
    
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
