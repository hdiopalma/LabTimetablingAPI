import unittest
import numpy as np
from django.test import TestCase
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.assistant_distribution import AssistantDistributionFitness

class TestAssistantDistributionFitness(TestCase):
    def setUp(self):
        self.fitness = AssistantDistributionFitness()
        self.fitness.configure(
            max_group_threshold=3,
            max_shift_threshold=4,
            group_penalty=2,
            shift_penalty=1
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
                    np.datetime64(gene["time_slot"].date).astype(float),  # Convert date to float
                    gene["time_slot"].day,
                    gene["time_slot"].shift
                )
            )
        return chromosome

    def extract_parameters(self, chromosome):
        """Extract numpy arrays from chromosome for penalty calculation"""
        return (
            chromosome.gene_data["module"],
            chromosome.gene_data["assistant"],
            chromosome.gene_data["group"],
            chromosome.gene_data["time_slot_date"],
            chromosome.gene_data["time_slot_shift"]
        )

    def test_no_penalties(self):
        """Test scenario with no penalties"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 2, "group": 2, "assistant": 2,
             "time_slot": TimeSlot(date='2023-01-02', day='Tuesday', shift='Afternoon')},
        ]
        chromosome = self.create_chromosome(genes)
        params = self.extract_parameters(chromosome)
        penalty = self.fitness.calculate_penalty(*params)
        self.assertEqual(penalty, 0)

    def test_group_limit_exceeded(self):
        """Test penalty for group count exceeding threshold"""
        genes = [
                {"lab": 1, "module": 1, "module_chapter": i, "group": i, "assistant": 1, 
                 "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')}
    for i in range(5)
]
        chromosome = self.create_chromosome(genes)
        params = self.extract_parameters(chromosome)
        penalty = self.fitness.calculate_penalty(*params)
        expected = (5 - 3) * 2  # Only group penalty now
        self.assertEqual(penalty, expected)

    def test_shift_limit_exceeded(self):
        """Test penalty for shift count exceeding threshold"""
        genes = [
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date=f'2023-01-0{i+1}', day='Monday', shift=f'Shift{i}')}
            for i in range(5)  # 5 unique shifts
        ]
        chromosome = self.create_chromosome(genes)
        params = self.extract_parameters(chromosome)
        penalty = self.fitness.calculate_penalty(*params)
        expected = (5 - 4) * 1  # (actual - threshold) * penalty
        self.assertEqual(penalty, expected)

    def test_combined_penalties(self):
        """Test combined group and shift penalties"""
        genes = [
            # Assistant 1: 4 groups, 5 shifts
            *[{"lab": 1, "module": 1, "module_chapter": i, "group": i, "assistant": 1,
               "time_slot": TimeSlot(date=f'2023-01-0{i+1}', day='Monday', shift=f'Shift{i}')} for i in range(5)],
            
            # Assistant 2: 2 groups, 3 shifts (no penalties)
            *[{"lab": 1, "module": 1, "module_chapter": i, "group": i+10, "assistant": 2,
               "time_slot": TimeSlot(date=f'2023-01-1{i+1}', day='Tuesday', shift=f'Shift{i}')} for i in range(3)],
        ]
        chromosome = self.create_chromosome(genes)
        params = self.extract_parameters(chromosome)
        penalty = self.fitness.calculate_penalty(*params)
        
        # Calculate expected penalties
        assistant1_penalty = (5 - 3)*2 + (5 - 4)*1 # (groups - threshold) * group_penalty + (shifts - threshold) * shift_penalty
        assistant2_penalty = 0
        self.assertEqual(penalty, assistant1_penalty + assistant2_penalty)

    def test_duplicate_entries(self):
        """Test that duplicate module+group or module+date+shift combinations don't count"""
        genes = [
            # Same module+group, different shifts
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Morning')},
            {"lab": 1, "module": 1, "module_chapter": 1, "group": 1, "assistant": 1,
             "time_slot": TimeSlot(date='2023-01-01', day='Monday', shift='Afternoon')},
        ]
        chromosome = self.create_chromosome(genes)
        params = self.extract_parameters(chromosome)
        penalty = self.fitness.calculate_penalty(*params)
        
        # Should count as 1 group, 2 shifts
        group_penalty = max(1 - 3, 0) * 2
        shift_penalty = max(2 - 4, 0) * 1
        self.assertEqual(penalty, group_penalty + shift_penalty)

class TimeSlot:
    """Helper class for test time slot creation"""
    def __init__(self, date, day, shift):
        self.date = date
        self.day = day
        self.shift = shift

if __name__ == '__main__':
    unittest.main()