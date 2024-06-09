#GroupAssignmentConflictPenalty
from collections import Counter
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness
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

    def __call__(self, timeslots, entity_ids, penalty):
        total_penalty = 0
        # combined_data = np.column_stack((timeslots, entity_ids))
        # unique_combinations, counts = np.unique(combined_data, return_counts=True, axis=0)
        combined_data = list(zip(timeslots, entity_ids))
        counts = Counter(combined_data).values()
        for count in counts:
            if count > 1:
                total_penalty += (count - 1) * penalty
        return total_penalty
    
    def calculate_penalty(self, assistants, groups, timeslots):
        assistant_penalty = self(timeslots, assistants, self.assistant_conflict_penalty)
        group_penalty = self(timeslots, groups, self.group_conflict_penalty)
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