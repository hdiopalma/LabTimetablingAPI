import random
import numpy as np
from datetime import timedelta, datetime

from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.data_parser import ModuleData, GroupData, Constant, CommonData
from scheduling_algorithm.operator.repair.base_repair import BaseRepair

from scheduling_algorithm.factory import timeslot_generator, timeslot_manager

class TimeSlotRepair(BaseRepair):
    """Kelas untuk memperbaiki timeslot yang bertabrakan pada jadwal asisten dan grup.

    Args:
        BaseRepair (class): Kelas dasar untuk fungsi repair.
    """
    def __init__(self):
        super().__init__("RepairTimeSlot")
        self.module_data = ModuleData
        self.group_data = GroupData

    def __call__(self, chromosome: Chromosome):
        week = chromosome.week
        
        timeslot_days = chromosome['time_slot_day']
        timeslot_shifts = chromosome['time_slot_shift']
        assistants = chromosome['assistant']
        groups = chromosome['group']
        
        conflicting_timeslots_mask = np.array([
            not CommonData.get_schedule(assistants[i], groups[i])[timeslot_days[i]][timeslot_shifts[i]]
            for i in range(len(timeslot_days))
        ])
        
        # Filter the chromosome for only the genes with conflicting timeslots
        conflicting_indices = np.where(conflicting_timeslots_mask)[0]
        
        for index in conflicting_indices:
            gene = chromosome.gene_data[index]
            start_date, end_date = timeslot_manager.get_date_range(gene["module"], week)
            available_time_slot = self._choose_available_time_slot(start_date, end_date, gene["group"], gene["assistant"])
            chromosome.set_time_slot(index, available_time_slot)
        
        return chromosome

    def _choose_available_time_slot(self, start_date: datetime, end_date: datetime, group_id:int, assistant_id:int = None):
        if start_date.weekday() != 0:
            start_date += timedelta(days=7 - start_date.weekday())
        available_time_slots = timeslot_generator.generate_available_time_slots(start_date, end_date, group_id, assistant_id)
        if not available_time_slots:
            return self._random_time_slot(start_date, end_date)
        return random.choice(available_time_slots)

    def _random_time_slot(self, start_date, end_date):
        if start_date.weekday() != 0:
            start_date += timedelta(days=7 - start_date.weekday())
        random_date = self._get_random_date(start_date, end_date)
        random_days = Constant.days[random_date.weekday()]
        random_shifts = random.choice(Constant.shifts)
        return (random_date.timestamp(), random_days, random_shifts)

    def _get_random_date(self, start_date, end_date):
        duration = (end_date - start_date).days
        random_date = start_date + timedelta(days=random.randint(0, duration))
        while random_date.weekday() == 6:  # Avoid Sunday
            random_date = start_date + timedelta(days=random.randint(0, duration))
        return random_date
