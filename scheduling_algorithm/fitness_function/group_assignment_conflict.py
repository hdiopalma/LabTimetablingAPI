#GroupAssignmentConflictPenalty
#path: scheduling_algorithm/fitness_function/group_assignment_conflict.py

from collections import defaultdict
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness
import numpy as np


class GroupAssignmentCapacityFitness(BaseFitness):

    def __init__(self):
        """Calculate penalty for exceeding the maximum number of groups that can be assigned to a single time slot in lab.
        (Maksimal jumlah kelompk yang diajar oleh asisten dalam satu waktu)
        """
        super().__init__("GroupAssignmentCapacityFitness")
        self.max_threshold = None
        self.conflict_penalty = None

    def __str__(self):
        return (
            f"Fitness(name={self.name}, max_threshold={self.max_threshold}, conflict_penalty={self.conflict_penalty})"
        )

    def calculate_penalty(self, modules, assistants, timeslot_dates,
                          timeslot_shifts):
        assistant_timeslot_count = defaultdict(int)
        total_penalty = 0

        for i in range(len(assistants)):
            combination = (assistants[i], timeslot_dates[i], timeslot_shifts[i]
                           )  # Hapus modules[i]
            assistant_timeslot_count[combination] += 1

        for count in assistant_timeslot_count.values():
            if count > self.max_threshold:
                total_penalty += (count -
                                  self.max_threshold) * self.conflict_penalty

        return total_penalty

    def calculate_penalty_with_violations(self, modules, assistants,
                                          timeslot_dates,
                                          timeslot_shifts) -> tuple:
        """Detailed calculation with violation tracking"""
        total = 0
        violations = defaultdict(int)

        assistant_timeslot_count = defaultdict(int)

        for i in range(len(assistants)):
            combination = (assistants[i], timeslot_dates[i],
                           timeslot_shifts[i])
            assistant_timeslot_count[combination] += 1
        for combination, count in assistant_timeslot_count.items():
            if count > self.max_threshold:
                excess_count = count - self.max_threshold
                violations[combination] = excess_count
                total += excess_count * self.conflict_penalty
        return total, violations

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
