import random
from math import floor
from datetime import timedelta, datetime
from collections import namedtuple
from functools import lru_cache

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import ModuleData, GroupData, Constant, CommonData
from scheduling_algorithm.operator.repair.base_repair import BaseRepair

from scheduling_algorithm.factory import timeslot_manager

# Simple data structure for timeslot
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])

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
        week = chromosome.week
        for index, gene in enumerate(chromosome):
            start_date, end_date = timeslot_manager.get_date_range(gene['module'], week)
            schedule = CommonData.get_schedule(gene['assistant'], gene['group'])
            if not schedule[gene['time_slot'].day][gene['time_slot'].shift]:
                time_slot = self._choose_available_time_slot(start_date, end_date, gene['group'], gene['assistant'])
                chromosome.set_time_slot(index, time_slot)
        return chromosome

    def _choose_available_time_slot(self, start_date: datetime, end_date: datetime, group_id:int, assistant_id:int = None):
        if start_date.weekday() != 0:
            start_date += timedelta(days=7 - start_date.weekday())
        available_time_slots = timeslot_manager.generate_available_time_slots(start_date, end_date, group_id, assistant_id)
        if not available_time_slots:
            return self._random_time_slot(start_date, end_date)
        return random.choice(available_time_slots)

    def _random_time_slot(self, start_date, end_date):
        if start_date.weekday() != 0:
            start_date += timedelta(days=7 - start_date.weekday())
        random_date = self._get_random_date(start_date, end_date)
        random_days = Constant.days[random_date.weekday()]
        random_shifts = random.choice(Constant.shifts)
        return TimeSlot(random_date.timestamp(), random_days, random_shifts)

    def _get_random_date(self, start_date, end_date):
        duration = (end_date - start_date).days
        random_date = start_date + timedelta(days=random.randint(0, duration))
        while random_date.weekday() == 6:  # Avoid Sunday
            random_date = start_date + timedelta(days=random.randint(0, duration))
        return random_date
