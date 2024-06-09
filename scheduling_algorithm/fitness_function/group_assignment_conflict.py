#GroupAssignmentConflictPenalty
from collections import Counter
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness
import numpy as np
import numba

@numba.jit(nopython=True)
def calculate_penalty_numba(labs, modules, assistants, timeslot_dates, timeslot_days, timeslot_shifts, penalty):
    total_penalty = 0
    seen = set()
    for i in range(len(labs)):
        key = (labs[i], modules[i], assistants[i], timeslot_dates[i], timeslot_days[i], timeslot_shifts[i])
        if key in seen:
            total_penalty += penalty
        else:
            seen.add(key)
    return total_penalty

class GroupAssignmentCapacityFitness(BaseFitness):
    def __init__(self):
        """Calculate penalty for exceeding the maximum number of groups that can be assigned to a single time slot in lab.
        (Maksimal jumlah kelompk yang diajar oleh asisten dalam satu waktu)
        """
        super().__init__("GroupAssignmentCapacityFitness")
        self.max_threshold = None
        self.conflict_penalty = None
        
    def __str__(self):
        message = f"Fitness(name={self.name}, max_threshold={self.max_threshold}, conflict_penalty={self.conflict_penalty})"
        return message

    def calculate_penalty(self, labs, modules, assistants, timeslot_dates, timeslot_days, timeslot_shifts):
        total_penalty = 0
        seen_combinations = set()
        for i in range(len(labs)):
            combination = (labs[i], modules[i], assistants[i], timeslot_dates[i], timeslot_days[i], timeslot_shifts[i])
            if combination in seen_combinations:
                total_penalty += self.conflict_penalty
            else:
                seen_combinations.add(combination)
        return total_penalty
        
        #-------------------#
        # return calculate_penalty_numba(labs, modules, assistants, timeslot_dates, timeslot_days, timeslot_shifts, self.conflict_penalty)
        total_penalty = 0
        # combined_data = np.column_stack((labs, modules, assistants, timeslot_dates, timeslot_days, timeslot_shifts))
        combined_data = np.concatenate((labs.reshape(-1, 1), modules.reshape(-1, 1), assistants.reshape(-1, 1), timeslot_dates.reshape(-1, 1), timeslot_days.reshape(-1, 1), timeslot_shifts.reshape(-1, 1)), axis=1)
        unique_combinations, counts = np.unique(combined_data, return_counts=True, axis=0)
        for count in counts:
            if count > self.max_threshold:
                excess = count - self.max_threshold
                total_penalty += excess * self.conflict_penalty
        return total_penalty
    
    def configure(self, max_threshold, conflict_penalty):
        """Configure the fitness function
        Args:
            max_threshold (int): Maximum number of groups that can be assigned to a single time slot in lab
            conflict_penalty (int): Penalty for each group that exceeds the maximum threshold"""
        self.max_threshold = max_threshold
        self.conflict_penalty = conflict_penalty
        return self
    
    @classmethod
    def create(cls, config):
        """Create GroupAssignmentConflictFitness instance from configuration
        Args:
            config (dict): Configuration for the fitness function
            config = {
                "max_threshold": 3,
                "conflict_penalty": 1
            }
        """
        fitness = cls().configure(**config)
        return fitness