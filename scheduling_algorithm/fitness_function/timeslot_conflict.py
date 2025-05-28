# GroupAssignmentConflictPenalty
# path: scheduling_algorithm/fitness_function/timeslot_conflict.py

from collections import defaultdict, Counter
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness


class TimeslotConflict(BaseFitness):

    def __init__(self):
        super().__init__("TimeslotConflictFitness")
        self.assistant_conflict_penalty = None
        self.group_conflict_penalty = None

    def __str__(self):
        return f"Fitness(name={self.name}, assistant_conflict_penalty={self.assistant_conflict_penalty}, group_conflict_penalty={self.group_conflict_penalty})"

    def __call__(self,
                 timeslot_dates,
                 timeslot_shifts,
                 entity_ids,
                 chapters,
                 penalty,
                 is_assistant=False):
        if is_assistant:
            # Track unique chapters per (date, shift, assistant)
            chapter_sets = defaultdict(set)
            for date, shift, entity_id, chapter in zip(timeslot_dates,
                                                       timeslot_shifts,
                                                       entity_ids, chapters):
                combination = (date, shift, entity_id)
                chapter_sets[combination].add(chapter)
            # Penalty is (number of unique chapters - 1) per combination
            return sum((len(chapters) - 1) * penalty
                       for chapters in chapter_sets.values())
        else:
            # Count occurrences of each (date, shift, group)
            counts = Counter(zip(timeslot_dates, timeslot_shifts, entity_ids))
            # Penalty is (count - 1) per combination
            return sum((count - 1) * penalty for count in counts.values())

    def calculate_penalty(self, assistants, groups, chapters, timeslot_dates,
                          timeslot_shifts):
        # Calculate penalties using optimized __call__
        assistant_penalty = self(timeslot_dates,
                                 timeslot_shifts,
                                 assistants,
                                 chapters,
                                 self.assistant_conflict_penalty,
                                 is_assistant=True)
        group_penalty = self(timeslot_dates,
                             timeslot_shifts,
                             groups,
                             chapters,
                             self.group_conflict_penalty,
                             is_assistant=False)
        return assistant_penalty + group_penalty

    def calculate_penalty_with_violations(self, assistants, groups, chapters,
                                          timeslot_dates,
                                          timeslot_shifts) -> tuple:
        """Detailed calculation with violation tracking"""
        total = 0
        violations = {
            "assistant_conflicts": defaultdict(int),
            "group_conflicts": defaultdict(int)
        }

        # Assistant conflicts
        assistant_chapters = defaultdict(set)
        for i in range(len(assistants)):
            key = (timeslot_dates[i], timeslot_shifts[i], assistants[i])
            assistant_chapters[key].add(chapters[i])

        for key, chaps in assistant_chapters.items():
            if len(chaps) > 1:
                count = len(chaps) - 1
                violations["assistant_conflicts"][key] = count
                total += count * self.assistant_conflict_penalty

        # Group conflicts
        group_counter = Counter()
        for i in range(len(groups)):
            key = (timeslot_dates[i], timeslot_shifts[i], groups[i])
            group_counter[key] += 1

        for key, count in group_counter.items():
            if count > 1:
                over = count - 1
                violations["group_conflicts"][key] = over
                total += over * self.group_conflict_penalty

        return total, violations

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
        """Create TimeslotConflict instance from configuration
        Args:
            config (dict): Configuration for the fitness function
            config = {
                "assistant_conflict_penalty": 5,
                "group_conflict_penalty": 2.5
            }
        """
        return cls().configure(**config)
