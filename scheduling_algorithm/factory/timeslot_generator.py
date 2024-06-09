import numpy as np
from scheduling_algorithm.data_parser import Constant
from scheduling_algorithm.data_parser import ModuleData, GroupData, CommonData
from scheduling_algorithm.structure import Chromosome
from scheduling_algorithm.factory import timeslot_manager

import random
from datetime import timedelta, datetime
from math import floor
from collections import defaultdict
import numpy as np
from functools import lru_cache

@lru_cache(maxsize=24)
def generate_empty_time_slots(start_date: datetime, end_date: datetime) -> list:
    """Returns a list of empty time slots based on the start and end date.
    Args:
        start_date (datetime): The start date of the time slot range.
        end_date (datetime): The end date of the time slot range.
        chapter_id (int): The chapter ID.
        assistant_id (int): The assistant ID.
    Returns:
        list: The available time slots.
    """
    empty_time_slots = []
    weeks_duration = max(1, floor(((end_date - start_date).days + 1) / 7))
    for week in range(weeks_duration):
        for day in Constant.days:
            for shift in Constant.shifts:
                date = (start_date + timedelta(days=week * 7 + Constant.days.index(day))).timestamp()
                timeslot = (date, day, shift)
                empty_time_slots.append(timeslot)
    return empty_time_slots

#Global cache for available time slots to avoid redundant computation
def generate_available_time_slots(start_date:datetime, end_date:datetime, group_id:int, assistant_id:int = None) -> list:
    """Generates the available time slots based on the group schedule.

    Args:
        start_date (datetime): The start date of the time slot range.
        end_date (datetime): The end date of the time slot range.
        group_id (int): The group ID.
        assistant_id (int): The assistant ID. Optional. If provided, the function will also check the assistant's schedule.

    Returns:
        list: The available time slots.
    """
    empty_time_slots = generate_empty_time_slots(start_date, end_date)
    schedule = CommonData.get_schedule(assistant_id, group_id) if assistant_id else GroupData.get_schedule(group_id)
    available_time_slots = [time_slot for time_slot in empty_time_slots if schedule[time_slot[1]][time_slot[2]]]
    return available_time_slots

def get_random_time_slot(module_id:int, group_id:int, assistant_id:int = None, week:int = 0) -> tuple:
    """Returns a random time slot based on the module and group.

    Args:
        module_id (int): The module ID.
        group_id (int): The group ID.
        assistant_id (int): The assistant ID. Optional. If provided, the function will also check the assistant's schedule.

    Returns:
        tuple: The random time slot.
    """
    start_date, end_date = timeslot_manager.get_date_range(module_id, week)
    available_time_slots = generate_available_time_slots(start_date, end_date, group_id, assistant_id)
    if not available_time_slots:
        return random.choice(timeslot_manager.get_all_time_slots())
    return random.choice(available_time_slots)

class TimeSlotGenerator:
    def __init__(self,start_date: datetime, end_date: datetime, max_capacity: int) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.max_capacity = max_capacity
        self.empty_time_slots = {}
        timeslot_manager.set_date_range(self.start_date, self.end_date)
        #To keep track of the capacity of the time slot
        #time_slot_capacities[assistant_id][chapter_id][time_slot] = int
        self.time_slot_capacities = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        #To make sure that the group is not assigned to the same time slot
        self.group_time_slots = defaultdict(list)
        self.assistant_time_slots = defaultdict(list)
        
        self.empty_time_slots = generate_empty_time_slots(self.start_date, self.end_date)
        
    def generate_time_slot(self, chapter_id, assistant_id, group_id) -> tuple:
        """Generates a time slot based on the availability of the assistant and the capacity of the time slot.
        Biased towards the data that has the same assistant and chapter.
        Args:
            chapter_id (int): The chapter ID.
            assistant_id (int): The assistant ID.
            max_capacity (int): The maximum capacity of the time slot.

        Returns:
            tuple: The time slot.
        """
        if self.time_slot_capacities[assistant_id][chapter_id]:
            time_slots = list(self.time_slot_capacities[assistant_id][chapter_id].keys())
            time_slots = [time_slot for time_slot in time_slots if self.time_slot_capacities[assistant_id][chapter_id][time_slot] < self.max_capacity]
            #shuffle the time slots
            if time_slots:
                np.random.shuffle(time_slots)
                for time_slot in time_slots:
                    if group_id not in self.group_time_slots[time_slot]:
                        self.add_group_to_time_slot(time_slot, chapter_id, group_id, assistant_id)
                        return time_slot
        time_slot = self.get_random_time_slot(group_id, assistant_id)
        self.add_group_to_time_slot(time_slot, chapter_id, group_id, assistant_id)
        return time_slot
    
    def add_group_to_time_slot(self, time_slot: tuple, chapter_id: int, group_id: int, assistant_id: int) -> bool:
        """Adds a group to the time slot capacity.

        Args:
            time_slot (tuple): The time slot.
            group_id (int): The group ID.
            chapter_id (int): The chapter ID.
            assistant_id (int): The assistant ID.
            
        Returns:
            bool: The success of adding the group to the time slot.
        """
        self.time_slot_capacities[assistant_id][chapter_id][time_slot] += 1
        self.group_time_slots[time_slot].append(group_id)
    
    def get_random_time_slot(self, group_id: int, assistant_id:int = None) -> tuple:
        """Returns a random time slot based on the chapter and assistant.

        Args:
            chapter_id (int): The chapter ID.
            assistant_id (int): The assistant ID.

        Returns:
            tuple: The random time slot.
        """
        available_time_slots = generate_available_time_slots(self.start_date, self.end_date, group_id, assistant_id)
        if not available_time_slots:
            return random.choice(self.empty_time_slots)
        
        for _ in range(100):
            time_slot = random.choice(available_time_slots)
            if group_id not in self.group_time_slots[time_slot] and assistant_id not in self.assistant_time_slots[time_slot]:
                self.assistant_time_slots[time_slot].append(assistant_id)
                self.group_time_slots[time_slot].append(group_id)
                return time_slot
        return random.choice(available_time_slots)

    
    def clear(self):
        """Clear the time slot capacities and group time slots.
        """
        self.time_slot_capacities = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.group_time_slots = defaultdict(list)
        

        
        