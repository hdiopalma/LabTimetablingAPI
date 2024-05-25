#factory.py
from math import ceil, floor
import random
from datetime import timedelta

from functools import lru_cache

import json

#Simple data structure for timeslot
from collections import namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])

from scheduling_algorithm.structure import Chromosome, Population
from scheduling_algorithm.fitness_function import FitnessManager, AssistantDistributionFitness, GroupAssignmentConflictFitness
from scheduling_algorithm.structure import Gene
from scheduling_algorithm.data_parser import *

from .timeslot_manager import TimeSlotManager

class Factory:
    '''Factory class to generate chromosomes and population. It also contains the data from the database.
    '''
    def __init__(self):
        self.laboratories = LaboratoryData
        self.modules = ModuleData
        self.chapters = ChapterData
        self.groups = GroupData
        self.participants = ParticipantData
        self.assistants = AssistantData
        self.constant = Constant
        
        self.time_slot_manager = TimeSlotManager()
        self.fitness_manager = FitnessManager([GroupAssignmentConflictFitness(), AssistantDistributionFitness()])

    def set_fitness_manager(self, fitness_manager: FitnessManager):
        self.fitness_manager = fitness_manager
    
    def generate_chromosome(self) -> Chromosome:
        """Generate a chromosome based on data, each group must be assigned to all chapters in a module of appropriate lab"""
        chromosome = Chromosome([])
        for module in self.modules.get_modules():
            try:
                self.time_slot_manager.generate_empty_time_slot(module.start_date, module.end_date, module.id, 3)
            except Exception as e:
                print(f"Error generating empty time slot: {e}")
                break
            for group in self.modules.get_groups(module.id):  
                for chapter in self.modules.get_chapters(module.id):
                    laboratory = module.laboratory
                    assistant = random.choice(self.laboratories.get_assistants(laboratory.id))
                    try:
                        time_slot = self.time_slot_manager.generate_available_time_slot(module.id, group.id, randomize=True)
                    except Exception as e:
                        print(f"Error generating time slot: {e}")
                        break
                    chromosome.add_gene(laboratory.id, module.id, chapter.id, group.id, assistant.id, time_slot)
        self.time_slot_manager.clear()
        return chromosome
    
    def generate_population(self, population_size: int, fitness_manager: FitnessManager = None) -> Population:
        """Generate a population based on the population size"""
        if fitness_manager:
            self.fitness_manager = fitness_manager
        return Population([self.generate_chromosome() for _ in range(population_size)], self.fitness_manager)
    
class WeeklyFactory(Factory):
    """Factory class to generate chromosomes and population in a weekly basis. 
    """
    def __init__(self, weeks, week, module_id):
        super().__init__()
        self.weeks = weeks
        self.week = week
        self.module = self.modules.get_module(module_id)
        
    def generate_chromosome(self, weeks, week) -> Chromosome:
        chromosome = Chromosome([])
        module = self.module
        start_date = module.start_date + timedelta(weeks=week - 1)
        end_date = start_date + timedelta(weeks=1)
        for group in self.modules.get_groups(module.id):
            for chapter in self.slice_chapters(weeks, week, module.id):
                laboratory = module.laboratory
                assistant = random.choice(self.laboratories.get_assistants(laboratory.id))
                time_slot = self.time_slot_manager.generate_random_time_slot(start_date=start_date, end_date=end_date)
                chromosome.add_gene(laboratory.id, module.id, chapter.id, group.id, assistant.id, time_slot)
                chromosome.set_week(week)
        self.time_slot_manager.clear()
        return chromosome
    
    #slice chapters evenly into weeks
    @lru_cache(maxsize=64)
    def slice_chapters(self, weeks, week, module_id) -> list:
        """Slice the chapters into weeks. For example, if weeks = 4, week = 1 will return the chapters for the first week (1/4 of the total chapters)

        Args:
            weeks (int): Total weeks the chapters will be divided into
            week (int): The week to get the chapters.

        Returns:
            list: List of chapters for the week
        """
        if week > weeks:
            raise Exception("Week cannot be greater than weeks")
        chapters = self.modules.get_chapters(module_id)
        chapter_count = chapters.count()
        chapter_per_week = ceil(chapter_count / weeks) # Example: 12 / 8 = 2 chapters per week
        start_index = (week - 1) * chapter_per_week # Example: (4 - 1) * 2 = 6
        end_index = min(week * chapter_per_week, chapter_count) # Example: min(4 * 2, 12) = 8
        return chapters[start_index:end_index]

    def generate_population(self, population_size: int, fitness_manager: FitnessManager = None) -> Population:
        """Generate a population based on the population size"""
        if fitness_manager:
            self.fitness_manager = fitness_manager
        chromosomes = []
        for _ in range(population_size):
            temp = self.generate_chromosome(weeks = self.weeks, week = self.week)
            if len(temp) != 0:
                chromosomes.append(temp)
        return Population(chromosomes, self.fitness_manager)