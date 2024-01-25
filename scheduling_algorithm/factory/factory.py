#factory.py
from math import ceil, floor
import random
from datetime import timedelta

#Simple data structure for timeslot
from collections import namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])

from scheduling_algorithm.structure import Chromosome, Population
from scheduling_algorithm.fitness_function import FitnessManager, AssistantDistributionFitness, GroupAssignmentConflictFitness
from scheduling_algorithm.structure import Gene
from scheduling_algorithm.data_parser import LaboratoryData, ModuleData, ChapterData, GroupData, ParticipantData, AssistantData, Constant

class Factory:
    '''Factory class to generate chromosomes and population. It also contains the data from the database. We can call this class when we need some of'''
    def __init__(self):
        self.laboratories = LaboratoryData
        self.modules = ModuleData
        self.chapters = ChapterData
        self.groups = GroupData
        self.participants = ParticipantData
        self.assistants = AssistantData
        self.constant = Constant
        
        self.fitness_manager = FitnessManager([GroupAssignmentConflictFitness(), AssistantDistributionFitness()])

    def set_fitness_manager(self, fitness_manager: FitnessManager):
        self.fitness_manager = fitness_manager

    def set_data(self, laboratories, modules, chapters, groups, participants, assistants):
        self.laboratories = laboratories
        self.modules = modules
        self.chapters = chapters
        self.groups = groups
        self.participants = participants
        self.assistants = assistants
    
    def generate_time_slot(self, start_date, end_date):
        """Generate time slots based on the start date, end date, days and shifts"""
        #if start_date not start from Monday, then start from the next Monday
        if start_date.weekday() != 0:
            start_date = start_date + timedelta(days=7 - start_date.weekday())
        duration = (end_date - start_date).days + 1
        weeks_duration = floor(duration / 7) # Number of weeks between start date and end date, using floor to make sure that the time slot does not exceed the end date
        random_weeks = random.randint(0, weeks_duration)
        random_days = random.choice(self.constant.days)
        random_shifts = random.choice(self.constant.shifts)
        random_date = start_date + timedelta(days=random_weeks * 7 + self.constant.days.index(random_days))
        return TimeSlot(random_date, random_days, random_shifts)
    
    def generate_time_slot_weekly(self, start_date, end_date):
        """Generate time slots based on the start date, end date, days and shifts"""
        if start_date.weekday() != 0:
            start_date = start_date + timedelta(days=7 - start_date.weekday())
        random_days = random.choice(self.constant.days)
        random_shifts = random.choice(self.constant.shifts)
        random_date = start_date + timedelta(days= 7 + self.constant.days.index(random_days))
        return TimeSlot(random_date, random_days, random_shifts)
    
    def generate_chromosome(self) -> Chromosome:
        """Generate a chromosome based on data, each group must be assigned to all chapters in a module of appropriate lab"""
        chromosome = Chromosome([])
        for module in self.modules.get_modules():
            for group in self.modules.get_groups(module.id):
                for chapter in self.modules.get_chapters(module.id):
                    laboratory = module.laboratory
                    assistant = random.choice(self.laboratories.get_assistants(laboratory.id))
                    time_slot = self.generate_time_slot(module.start_date, module.end_date)
                    chromosome.add_gene(laboratory.id, module.id, chapter.id, group.id, assistant.id, time_slot)
        return chromosome
    
    def generate_chromosome_weekly(self) -> Chromosome:
        """Generate a chromosome based on data, each group must be assigned to all chapters in a module of appropriate lab"""
        chromosome = Chromosome([])
        for module in self.modules.get_modules():
            for group in self.modules.get_groups(module.id):
                start_date = module.start_date
                end_date = module.end_date
                duration = (end_date - start_date).days + 1
                weeks_duration = floor(duration / 7)
                chapters_count = len(self.modules.get_chapters(module.id))
                weekly_chapters = ceil(chapters_count / weeks_duration)
                for i in range(weekly_chapters):
                    laboratory = module.laboratory
                    assistant = random.choice(self.laboratories.get_assistants(laboratory.id))
                    time_slot = self.generate_time_slot_weekly(start_date, end_date)
                    #first chapter
                    chapter = module.chapters.all().first()
                    gene = Gene(laboratory.id, module.id, chapter.id, group.id)
                    chromosome.add_gene(gene=gene, assistant=assistant.id, time_slot=time_slot)
        return chromosome
    
    def generate_population(self, population_size: int, fitness_manager: FitnessManager = None, weekly = False) -> Population:
        """Generate a population based on the population size"""

        if fitness_manager:
            self.fitness_manager = fitness_manager

        if weekly:
            return Population([self.generate_chromosome_weekly() for _ in range(population_size)], self.fitness_manager)
        else:
            return Population([self.generate_chromosome() for _ in range(population_size)], self.fitness_manager)
    
