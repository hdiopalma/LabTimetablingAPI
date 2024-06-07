#GroupAssignmentConflictPenalty
from collections import defaultdict
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

class GroupAssignmentCapacityFitness(BaseFitness):
    def __init__(self):
        """Calculate penalty for exceeding the maximum number of groups that can be assigned to a single time slot in lab
        """
        super().__init__("GroupAssignmentCapacityFitness")
        self.max_threshold = 3
        self.conflict_penalty = 1
        
    def __str__(self):
        message = f"Fitness(name={self.name}, max_threshold={self.max_threshold}, conflict_penalty={self.conflict_penalty})"
        return message

    def calculate_penalty(self, capacity):
        total_penalty = 0
        for laboratory in capacity:
            for module in capacity[laboratory]:
                for time_slot in capacity[laboratory][module]:
                    groups = capacity[laboratory][module][time_slot]
                    if len(groups) > self.max_threshold:
                        total_penalty += (len(groups) - self.max_threshold) * self.conflict_penalty
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