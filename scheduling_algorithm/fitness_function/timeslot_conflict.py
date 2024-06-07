#GroupAssignmentConflictPenalty
from collections import defaultdict
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

class TimeslotConflict(BaseFitness):
    def __init__(self):
        """Fitness function to penalize conflicts in timeslot assignment. (e.g. a group or assistant is assigned to the same timeslot more than once)
        """
        super().__init__("TimeslotConflictFitness")
        self.assistant_conflict_penalty = 5
        self.group_conflict_penalty = 2.5
        
    def __str__(self):
        message = f"Fitness(name={self.name}, assistant_conflict_penalty={self.assistant_conflict_penalty}, group_conflict_penalty={self.group_conflict_penalty})"
        return message

    def calculate_penalty(self, assistant_timeslots, group_timeslots):
        total_penalty = 0
        total_penalty += sum(
            self.assistant_conflict_penalty for assistants in assistant_timeslots.values()
            for count in assistants.values() if count > 1
        )

        # Calculate group conflicts
        total_penalty += sum(
            self.group_conflict_penalty for groups in group_timeslots.values()
            for count in groups.values() if count > 1
        )
        
        return total_penalty
    
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