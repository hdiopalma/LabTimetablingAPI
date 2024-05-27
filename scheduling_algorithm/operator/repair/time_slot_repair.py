import random
from math import floor
from datetime import timedelta, datetime

#Simple data structure for timeslot
from collections import namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import ModuleData, GroupData, Constant
from scheduling_algorithm.factory.timeslot_manager_backup import TimeSlotManager

from scheduling_algorithm.operator.repair.base_repair import BaseRepair

class TimeSlotRepair(BaseRepair):
    def __init__(self):
        super().__init__("RepairTimeSlot")
        self.module_data = ModuleData
        self.group_data = GroupData
    
    def __call__(self, chromosome: Chromosome):
        """
        Repairs the time slots in the given chromosome by checking the availability of time slots based on the schedule of the group.

        Args:
            chromosome (Chromosome): The chromosome to be repaired.

        Returns:
            Chromosome: The repaired chromosome.
        """
        if chromosome.week == 0:
            return self.repair(chromosome)
        return self.repair_weekly(chromosome, chromosome.week)
    
    def repair(self, chromosome: Chromosome):
        for index, gene in enumerate(chromosome):
            start_date = self.module_data.get_dates(gene['module']).start_date
            end_date = self.module_data.get_dates(gene['module']).end_date
            schedule = self.group_data.get_schedule(gene['group'])
            if not self.check_available_time_slot(gene['time_slot'], schedule):
                time_slot = self.find_feasible_solution(start_date, end_date, schedule)
                if time_slot is None:
                    time_slot = gene['time_slot']
                chromosome.set_time_slot(index, time_slot)
        return chromosome
    
    def repair_weekly(self, chromosome: Chromosome, week: int):
        for index, gene in enumerate(chromosome):
            start_date = self.module_data.get_dates(gene['module']).start_date + timedelta(weeks=week - 1)
            end_date = start_date + timedelta(weeks=1)
            schedule = self.group_data.get_schedule(gene['group'])
            if not self.check_available_time_slot(gene['time_slot'], schedule):
                time_slot = self.find_feasible_solution(start_date, end_date, schedule)
                if time_slot is None:
                    time_slot = gene['time_slot']
                chromosome.set_time_slot(index, time_slot)
                # print(f"Start Date: {start_date}, End Date: {end_date}")
                # print(f"Chapter: {gene['chapter']}, Group: {gene['group']}, Module: {gene['module']}, Time Slot: {datetime.fromtimestamp(time_slot.date)}")
                # print("=====================================")
    def check_available_time_slot(self,time_slot: TimeSlot, schedule=None):
        if schedule:
            return schedule[time_slot.day][time_slot.shift]
        return False
    
    def find_feasible_solution(self, start_date, end_date, schedule, max_iteration=100):
        """Find a feasible solution for the gene by randomly generating a time slot until it is available"""
        for _ in range(max_iteration):
            time_slot = self.choose_available_time_slot(start_date, end_date, schedule)
            if self.check_available_time_slot(time_slot, schedule):
                return time_slot
        return None
    
    def choose_available_time_slot(self,start_date: datetime, end_date: datetime, schedule):
        """Choose a random available time slot for the gene"""
        if start_date.weekday() != 0:
            start_date = start_date + timedelta(days=7 - start_date.weekday())
        week_duration = floor(((end_date - start_date).days + 1) / 7)
        available_time_slots = [TimeSlot(start_date, day, shift) for day, shifts in schedule.items() for shift, available in shifts.items() if available]
        #if there is no available time slot, then return a random time slot
        if len(available_time_slots) == 0:
            return self.generate_time_slot(start_date, end_date)
        random_time_slot = random.choice(available_time_slots)
        random_week = 0 if week_duration == 1 else random.randint(0, week_duration)
        #calculate the date
        random_date = start_date + timedelta(days=random_week * 7 + Constant.days.index(random_time_slot.day))
        random_date = random_date.timestamp()
        return TimeSlot(random_date, random_time_slot.day, random_time_slot.shift)
    
    def generate_time_slot(self, start_date, end_date):
        """Generate time slots based on the start date, end date, days and shifts"""
        return TimeSlotManager.generate_random_time_slot(start_date, end_date)