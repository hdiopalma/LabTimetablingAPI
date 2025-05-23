# Revised test cases for TimeslotConflict (Corrected Version)
import unittest
from django.test import TestCase
import numpy as np
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.timeslot_conflict import TimeslotConflict

class TestTimeslotConflict(TestCase):
    def setUp(self):
        self.fitness = TimeslotConflict()
        self.fitness.configure(
            assistant_conflict_penalty=5,
            group_conflict_penalty=2
        )
        
    def create_chromosome(self, genes):
        """Helper to create a Chromosome with test genes"""
        chromosome = Chromosome()
        for gene in genes:
            chromosome.add_gene(
                laboratory=gene["lab"],
                module=gene["module"],
                chapter=gene["module_chapter"],
                group=gene["group"],
                assistant=gene["assistant"],
                time_slot=(
                    np.datetime64(gene["time_slot"].date).astype(float),
                    gene["time_slot"].day,
                    gene["time_slot"].shift
                )
            )
        return chromosome

    def extract_parameters(self, chromosome):
        """Extract parameters in order needed by TimeslotConflict"""
        return (
            chromosome.gene_data["time_slot_date"],
            chromosome.gene_data["time_slot_shift"],
            chromosome.gene_data["group"],
            chromosome.gene_data["assistant"],
            chromosome.gene_data["chapter"]
        )

    def test_valid_schedule_no_penalties(self):
        """Test scenario with no conflicts"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 2,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Afternoon')},
        ]
        chromosome = self.create_chromosome(genes)
        dates, shifts, groups, assistants, chapters = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(assistants, groups, chapters, dates, shifts)
        self.assertEqual(penalty, 0)  # Tidak ada konflik

    def test_group_conflict_penalty(self):
        """Test penalty for SAME GROUP in same timeslot"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 1,  # Group sama!
             "assistant": 2,  # Asisten berbeda tidak berpengaruh
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        dates, shifts, groups, assistants, chapters = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(assistants, groups, chapters, dates, shifts)
        # 1 group conflict (group 1 duplikat) * penalty 2 = 2
        self.assertEqual(penalty, 2)

    def test_assistant_same_chapter_allowed(self):
        """Test NO penalty when assistant teaches SAME CHAPTER to multiple groups"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 2, "assistant": 1,  # Chapter sama
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        dates, shifts, groups, assistants, chapters = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(assistants, groups, chapters, dates, shifts)
        # Tidak ada penalti karena:
        # - Asisten mengajar chapter yang sama (0 penalty)
        # - Group berbeda di timeslot sama (diperbolehkan, 0 penalty)
        self.assertEqual(penalty, 0)

    def test_assistant_different_chapter_conflict(self):
        """Test penalty when assistant teaches DIFFERENT chapters in same timeslot"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 1,  # Chapter berbeda
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        dates, shifts, groups, assistants, chapters = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(assistants, groups, chapters, dates, shifts)
        # 1 assistant conflict (chapter berbeda) * penalty 5 = 5
        # Group berbeda di timeslot sama: tidak kena penalty
        self.assertEqual(penalty, 5)

    def test_mixed_valid_and_invalid(self):
        """Test combination of valid and invalid entries"""
        genes = [
            # Valid: Grup 1 dan Asisten 1 di timeslot 1 (chapter 1)
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            
            # Valid: Grup 2 dan Asisten 2 di timeslot 2 (tidak ada konflik)
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 2,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Afternoon')},
            
            # Invalid: Grup 1 di timeslot 1 lagi (group conflict)
            {"lab": 1, "module": 1, "module_chapter": 3, "group": 1, "assistant": 3,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            
            # Invalid: Asisten 1 di timeslot 1 dengan chapter berbeda
            {"lab": 1, "module": 1, "module_chapter": 4, "group": 3, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        dates, shifts, groups, assistants, chapters = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(assistants, groups, chapters, dates, shifts)
        # Breakdown:
        # - Group conflict: Grup 1 muncul 2x di timeslot 1 → 1 penalty (2)
        # - Assistant conflict: Asisten 1 mengajar 2 chapter berbeda di timeslot 1 → 1 penalty (5)
        # Total: 2 + 5 = 7
        self.assertEqual(penalty, 7)

    def test_multiple_groups_same_timeslot_no_penalty(self):
        """Test multiple DIFFERENT groups in same timeslot (allowed)"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 2, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 3, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        dates, shifts, groups, assistants, chapters = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(assistants, groups, chapters, dates, shifts)
        # Tidak ada penalty karena:
        # - Semua grup berbeda (group 1,2,3) → tidak ada group conflict
        # - Asisten mengajar chapter yang sama → tidak ada assistant conflict
        self.assertEqual(penalty, 0)

class TimeSlot:
    """Helper class for test time slot creation"""
    def __init__(self, date, day, shift):
        self.date = date
        self.day = day
        self.shift = shift
        
if __name__ == "__main__":
    unittest.main()