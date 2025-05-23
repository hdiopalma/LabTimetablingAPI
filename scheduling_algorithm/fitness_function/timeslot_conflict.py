#GroupAssignmentConflictPenalty
#path: scheduling_algorithm/fitness_function/timeslot_conflict.py

from collections import defaultdict
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

    def __call__(self, timeslot_dates, timeslot_shifts, entity_ids, chapters, penalty, is_assistant=False):
        total_penalty = 0
        seen_combinations = defaultdict(set)
        
        if is_assistant:
            # Check for conflicts where the same assistant is assigned the same timeslot for different chapters
            for i in range(len(timeslot_dates)):
                combination = (timeslot_dates[i], timeslot_shifts[i], entity_ids[i])
                if combination in seen_combinations and chapters[i] not in seen_combinations[combination]:
                    total_penalty += penalty  # Penalize duplicate
                else:
                    seen_combinations[combination].add(chapters[i])
        else:
            # Check for conflicts where the same group is assigned the same timeslot
            for i in range(len(timeslot_dates)):
                combination = (timeslot_dates[i], timeslot_shifts[i], entity_ids[i])
                if combination in seen_combinations:
                    total_penalty += penalty  # Penalize duplicate
                else:
                    seen_combinations[combination].add(chapters[i])
        
        return total_penalty
    
    def calculate_penalty(self, assistants, groups, chapters, timeslot_dates, timeslot_shifts):
        # Check for assistant conflicts
        assistant_penalty = self(timeslot_dates, timeslot_shifts, assistants, chapters, self.assistant_conflict_penalty, is_assistant=True)
        
        # Check for group conflicts
        group_penalty = self(timeslot_dates, timeslot_shifts, groups, chapters, self.group_conflict_penalty, is_assistant=False)
        
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