#GroupAssignmentConflictPenalty
from collections import Counter
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

import numpy as np
import numba

@numba.jit(nopython=True)
def calculate_penalty_numba(timeslot_dates, timeslot_days, timeslot_shifts, entity_ids, penalty):
    total_penalty = 0
    seen = set()
    for i in range(len(timeslot_dates)):
        key = (timeslot_dates[i], timeslot_days[i], timeslot_shifts[i], entity_ids[i])
        if key in seen:
            total_penalty += penalty
        else:
            seen.add(key)
    return total_penalty
class TimeslotConflict(BaseFitness):
    def __init__(self):
        """Fitness function to penalize conflicts in timeslot assignment. (e.g. a group or assistant is assigned to the same timeslot more than once)
        """
        super().__init__("TimeslotConflictFitness")
        self.assistant_conflict_penalty = None
        self.group_conflict_penalty = None
        
    def __str__(self):
        message = f"Fitness(name={self.name}, assistant_conflict_penalty={self.assistant_conflict_penalty}, group_conflict_penalty={self.group_conflict_penalty})"
        return message

    def __call__(self, timeslot_dates, timeslot_days, timeslot_shifts,  entity_ids, penalty):
        
        total_penalty = 0
        seen_combinations = set()
        for i in range(len(timeslot_dates)):
            combination = (timeslot_dates[i], timeslot_days[i], timeslot_shifts[i], entity_ids[i])
            if combination in seen_combinations:
                total_penalty += penalty  # Penalize duplicate
            else:
                seen_combinations.add(combination)
        return total_penalty
        
        #-------------------#
        # return calculate_penalty_numba(timeslot_dates, timeslot_days, timeslot_shifts, entity_ids, penalty)
        total_penalty = 0
        # combined_data = np.column_stack((timeslot_dates, timeslot_days, timeslot_shifts, entity_ids))
        combined_data = np.concatenate((timeslot_dates.reshape(-1, 1), timeslot_days.reshape(-1, 1), timeslot_shifts.reshape(-1, 1), entity_ids.reshape(-1, 1)), axis=1)
        unique_combinations, counts = np.unique(combined_data, return_counts=True, axis=0)
        for count in counts:
            if count > 1:
                total_penalty += (count - 1) * penalty
        return total_penalty
    
    def calculate_penalty(self, assistants, groups, timeslot_dates, timeslot_days, timeslot_shifts):
        assistant_penalty = self(timeslot_dates, timeslot_days, timeslot_shifts, assistants, self.assistant_conflict_penalty)
        group_penalty = self(timeslot_dates, timeslot_days, timeslot_shifts, groups, self.group_conflict_penalty)
        return assistant_penalty + group_penalty
    
    def configure(self, assistant_conflict_penalty, group_conflict_penalty):
        """Configure the fitness function
        Args:
            max_threshold (int): Maximum number of groups that can be assigned to a single time slot in lab
            conflict_penalty (int): Penalty for each group that exceeds the maximum threshold"""
        self.assistant_conflict_penalty = assistant_conflict_penalty
        self.group_conflict_penalty = group_conflict_penalty
        return self
    
    @classmethod
    def create(cls, config):
        """Create GroupAssignmentConflictFitness instance from configuration
        Args:
            config (dict): Configuration for the fitness function
            config = {
                "assistant_conflict_penalty": 5,
                "group_conflict_penalty": 2.5
            }
        """
        fitness = cls().configure(**config)
        return fitness