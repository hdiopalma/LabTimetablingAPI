import random
from math import floor
from datetime import timedelta, datetime
from collections import namedtuple
from functools import lru_cache

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import ModuleData, GroupData, Constant
from scheduling_algorithm.factory.timeslot_manager_backup import TimeSlotManager
from scheduling_algorithm.operator.repair.base_repair import BaseRepair

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
            start_date, end_date = self._get_date_range(gene, week)
            schedule = self.group_data.get_schedule(gene['group'])
            if not self._is_time_slot_available(gene['time_slot'], schedule):
                time_slot = self._find_feasible_solution(start_date, end_date, schedule, gene['group'])
                if time_slot is None:
                    time_slot = gene['time_slot']
                chromosome.set_time_slot(index, time_slot)
        self._clear_cache()
        return chromosome

    def _get_date_range(self, gene, week):
        start_date = self.module_data.get_dates(gene['module']).start_date
        if week > 0:
            start_date += timedelta(weeks=week - 1)
            end_date = start_date + timedelta(weeks=1)
        else:
            end_date = self.module_data.get_dates(gene['module']).end_date
        return start_date, end_date

    def _is_time_slot_available(self, time_slot: TimeSlot, schedule=None):
        return schedule and schedule[time_slot.day][time_slot.shift]

    def _find_feasible_solution(self, start_date, end_date, schedule, group_id, max_iteration=100):
        for _ in range(max_iteration):
            time_slot = self._choose_available_time_slot(start_date, end_date, group_id)
            if self._is_time_slot_available(time_slot, schedule):
                return time_slot
        return None

    def _choose_available_time_slot(self, start_date: datetime, end_date: datetime, group_id):
        if start_date.weekday() != 0:
            start_date += timedelta(days=7 - start_date.weekday())
        available_time_slots = self.available_time_slots(start_date, end_date, group_id)
        if not available_time_slots:
            return self._generate_time_slot(start_date, end_date)
        return random.choice(available_time_slots)

    @lru_cache(maxsize=48)
    def available_time_slots(self, start_date, end_date, group_id):
        available_time_slots = []
        schedule = self.group_data.get_schedule(group_id)
        week_duration = max(1, floor(((end_date - start_date).days + 1) / 7))
        for week in range(week_duration):
            for day, shifts in schedule.items():
                for shift, available in shifts.items():
                    if available:
                        date = start_date + timedelta(days=week * 7 + Constant.days.index(day))
                        available_time_slots.append(TimeSlot(date.timestamp(), day, shift))
        return available_time_slots

    def _generate_time_slot(self, start_date, end_date):
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("The start date and end date must be in datetime format.")
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

    def _clear_cache(self):
        self.available_time_slots.cache_clear()
