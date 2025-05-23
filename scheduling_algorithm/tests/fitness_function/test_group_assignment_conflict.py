# test_group_assignment_capacity.py
import unittest
from django.test import TestCase
import numpy as np
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.group_assignment_conflict import GroupAssignmentCapacityFitness

class TestGroupAssignmentCapacityFitness(TestCase):
    def setUp(self):
        self.fitness = GroupAssignmentCapacityFitness()
        self.fitness.configure(
            max_threshold=3,  # Maksimal 3 grup per asisten per timeslot
            conflict_penalty=1  # Penalty 1 per kelebihan grup
        )
        
    def create_chromosome(self, genes):
        """Helper untuk membuat kromosom uji"""
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
        """Ekstrak parameter untuk calculate_penalty"""
        return (
            chromosome.gene_data["module"],
            chromosome.gene_data["assistant"],
            chromosome.gene_data["time_slot_date"],
            chromosome.gene_data["time_slot_shift"]
        )

    def test_valid_capacity_no_penalty(self):
        """Test skenario dimana asisten tidak melebihi kapasitas"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 1, "group": 3, "assistant": 1,  # Modul berbeda
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        modules, assistants, dates, shifts = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(modules, assistants, dates, shifts)
        self.assertEqual(penalty, 0)  # Tepat di batas 3 grup

    def test_single_capacity_exceedance(self):
        """Test kelebihan 1 grup pada satu timeslot"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 3, "group": 3, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 1, "group": 4, "assistant": 1,  # Kelebihan 1
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        modules, assistants, dates, shifts = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(modules, assistants, dates, shifts)
        self.assertEqual(penalty, 1)  # (4-3)*1 = 1

    def test_multiple_timeslot_exceedances(self):
        """Test kelebihan di beberapa timeslot berbeda"""
        genes = [
            # Timeslot 1: 4 grup (kelebihan 1)
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 3, "group": 3, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 1, "group": 4, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            
            # Timeslot 2: 5 grup (kelebihan 2)
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 5, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 6, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 3, "group": 7, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 1, "group": 8, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 2, "group": 9, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        modules, assistants, dates, shifts = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(modules, assistants, dates, shifts)
        self.assertEqual(penalty, 3)  # (1 + 2) = 3

    def test_multiple_assistants(self):
        """Test beberapa asisten dengan kelebihan berbeda"""
        genes = [
            # Asisten 1: 4 grup di timeslot 1 (kelebihan 1)
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 3, "group": 3, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 1, "group": 4, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            
            # Asisten 2: 2 grup di timeslot 1 (aman)
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 5, "assistant": 2,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 6, "assistant": 2,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            
            # Asisten 3: 5 grup di timeslot 2 (kelebihan 2)
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 7, "assistant": 3,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 8, "assistant": 3,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 3, "group": 9, "assistant": 3,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 1, "group": 10, "assistant": 3,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 2, "group": 11, "assistant": 3,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        modules, assistants, dates, shifts = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(modules, assistants, dates, shifts)
        self.assertEqual(penalty, 3)  # Asisten 1:1 + Asisten 3:2 = 3

    def test_edge_case_exact_threshold(self):
        """Test kasus dimana jumlah grup persis di batas maksimal"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 2, "module_chapter": 1, "group": 3, "assistant": 1,  # Tepat di batas
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
        ]
        chromosome = self.create_chromosome(genes)
        modules, assistants, dates, shifts = self.extract_parameters(chromosome)
        
        penalty = self.fitness.calculate_penalty(modules, assistants, dates, shifts)
        self.assertEqual(penalty, 0)  # Tepat di batas, tidak ada penalty

class TimeSlot:
    """Helper class untuk membuat time slot"""
    def __init__(self, date, day, shift):
        self.date = date
        self.day = day
        self.shift = shift

if __name__ == "__main__":
    unittest.main()