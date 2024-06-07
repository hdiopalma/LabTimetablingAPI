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
from scheduling_algorithm.fitness_function import FitnessManager, AssistantDistributionFitness, GroupAssignmentCapacityFitness
from scheduling_algorithm.structure import Gene
from scheduling_algorithm.data_parser import *

from scheduling_algorithm.factory.timeslot_generator import TimeSlotGenerator
from scheduling_algorithm.factory import timeslot_manager

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
        
        self.module = None
        
        self.time_slot_generator = None
        self.fitness_manager = FitnessManager([GroupAssignmentCapacityFitness(), AssistantDistributionFitness()])

    def set_fitness_manager(self, fitness_manager: FitnessManager):
        self.fitness_manager = fitness_manager
    
    def generate_chromosome(self) -> Chromosome:
        """Generate a chromosome based on data, each group must be assigned to all chapters in a module of appropriate lab"""
        chromosome = Chromosome([])
        module = self.module
        for group in self.modules.get_groups(module.id):  
            for chapter in self.modules.get_chapters(module.id):
                laboratory = module.laboratory
                assistant = random.choice(self.laboratories.get_assistants(laboratory.id))
                try:
                    time_slot = self.time_slot_generator.generate_time_slot(chapter_id=chapter.id, assistant_id=assistant.id, group_id=group.id)
                except Exception as e:
                    print(f"Error generating time slot: {e}")
                    break
                chromosome.add_gene(laboratory.id, module.id, chapter.id, group.id, assistant.id, time_slot)
        self.time_slot_generator.clear()
        return chromosome
    
    def generate_population(self, population_size: int, module_id:int, fitness_manager: FitnessManager = None) -> Population:
        """Generate a population based on the population size"""
        self.module = self.modules.get_module(module_id)
        start_date, end_date = timeslot_manager.get_date_range(module_id)
        timeslot_manager.set_date_range(start_date, end_date)
        self.time_slot_generator = TimeSlotGenerator(start_date=start_date, end_date=end_date, max_capacity=3)
        if fitness_manager:
            self.fitness_manager = fitness_manager
        return Population([self.generate_chromosome() for _ in range(population_size)], self.fitness_manager)
    
class WeeklyFactory(Factory):
    """Factory class to generate chromosomes and population in a weekly basis. 
    """
    def __init__(self, weeks, week):
        super().__init__()
        self.weeks = weeks
        self.week = week
        self.module = None
        self.start_date = None
        self.end_date = None
        
    def generate_chromosome(self, weeks, week) -> Chromosome:
        gene = []
        module = self.module
        for group in self.modules.get_groups(module.id):
            for chapter in self.slice_chapters(weeks, week, module.id):
                laboratory = module.laboratory
                assistant = random.choice(self.laboratories.get_assistants(laboratory.id))
                # time_slot = self.time_slot_manager.generate_time_slot(chapter_id=chapter.id, assistant_id=assistant.id, group_id=group.id)
                time_slot = self.time_slot_generator.get_random_time_slot(group_id=group.id, assistant_id=assistant.id)
                gene.append({"laboratory": laboratory.id, "module": module.id, "chapter": chapter.id, "group": group.id, "assistant": assistant.id, "time_slot": time_slot})
             
        chromosome = Chromosome(gene)      
        self.time_slot_generator.clear()
        chromosome.set_week(week)
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

    def generate_population(self, population_size: int, module_id:int, fitness_manager: FitnessManager = None) -> Population:
        """Generate a population based on the population size"""
        
        #initialize the factory
        self.module = self.modules.get_module(module_id)
        self.start_date, self.end_date = timeslot_manager.get_date_range(module_id, self.week)
        self.time_slot_generator = TimeSlotGenerator(start_date=self.start_date, end_date=self.end_date, max_capacity=3)
        
        if fitness_manager:
            self.fitness_manager = fitness_manager
        chromosomes = []
        for _ in range(population_size):
            temp = self.generate_chromosome(weeks = self.weeks, week = self.week)
            if len(temp) != 0:
                chromosomes.append(temp)
        return Population(chromosomes, self.fitness_manager)