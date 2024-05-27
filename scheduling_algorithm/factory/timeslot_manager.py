
from collections import namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"]) #Simple data structure for timeslot, for reference

import numpy as np

from scheduling_algorithm.data_parser import Constant
from scheduling_algorithm.data_parser import ModuleData, GroupData

from scheduling_algorithm.structure import Chromosome

import random
from datetime import timedelta, datetime
from math import floor
from collections import defaultdict

import numpy as np

class TimeSlotManager:
    def __init__(self,start_date: datetime, end_date: datetime, max_capacity: int) -> None:
        self.max_capacity = max_capacity
        self.empty_time_slots = {}
        
        #To keep track of the capacity of the time slot
        #time_slot_capacities[assistant_id][chapter_id][time_slot] = int
        self.time_slot_capacities = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        #To make sure that the group is not assigned to the same time slot
        #group_time_slots[timeslot] = [group_id]
        self.group_time_slots = defaultdict(list)
        
        self.generate_empty_time_slots(start_date, end_date)
        
    def generate_time_slot(self, chapter_id, assistant_id, group_id) -> TimeSlot:
        """Generates a time slot based on the availability of the assistant and the capacity of the time slot.
        Biased towards the data that has the same assistant and chapter.
        Args:
            chapter_id (int): The chapter ID.
            assistant_id (int): The assistant ID.
            max_capacity (int): The maximum capacity of the time slot.

        Returns:
            TimeSlot: The generated time slot.
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
        time_slot = self.get_random_time_slot(group_id)
        self.add_group_to_time_slot(time_slot, chapter_id, group_id, assistant_id)
        return time_slot
    
    def add_group_to_time_slot(self, time_slot: TimeSlot, chapter_id: int, group_id: int, assistant_id: int) -> bool:
        """Adds a group to the time slot capacity.

        Args:
            time_slot (TimeSlot): The time slot.
            group_id (int): The group ID.
            chapter_id (int): The chapter ID.
            assistant_id (int): The assistant ID.
            
        Returns:
            bool: The success of adding the group to the time slot.
        """
        self.time_slot_capacities[assistant_id][chapter_id][time_slot] += 1
        self.group_time_slots[time_slot].append(group_id)    
    
    def generate_empty_time_slots(self, start_date: datetime, end_date: datetime) -> list:
        """Returns the available time slots based on the chapter and assistant.

        Args:
            start_date (datetime): The start date of the time slot range.
            end_date (datetime): The end date of the time slot range.
            chapter_id (int): The chapter ID.
            assistant_id (int): The assistant ID.

        Returns:
            list: The available time slots.
        """
        available_time_slots = []
        duration = (end_date - start_date).days + 1
        weeks_duration = floor(duration / 7)
        if weeks_duration == 0:
            weeks_duration = 1
        for week in range(weeks_duration):
            for day in Constant.days:
                for shift in Constant.shifts:
                    date = (start_date + timedelta(days=week * 7 + Constant.days.index(day))).timestamp()
                    timeslot = TimeSlot(date, day, shift)
                    available_time_slots.append(timeslot)
        self.empty_time_slots = available_time_slots
    
    def get_random_time_slot(self, group_id: int, max_iterations: int = 50) -> TimeSlot:
        """Returns a random time slot based on the chapter and assistant.

        Args:
            chapter_id (int): The chapter ID.
            assistant_id (int): The assistant ID.

        Returns:
            TimeSlot: The random time slot.
        """
        for _ in range(max_iterations):
            time_slot = random.choice(self.empty_time_slots)
            if self.check_availibility(time_slot, group_id):
                return time_slot
        return random.choice(self.empty_time_slots)
    
    def check_availibility(self, time_slot: TimeSlot, group_id: int) -> bool:
        """Checks the availability of the time slot based on the group schedule.

        Args:
            time_slot (TimeSlot): The time slot to be checked.
            group_id (int): The group ID.

        Returns:
            bool: The availability of the time slot.
        """
        group_schedule = GroupData.get_schedule(group_id)
        return group_schedule[time_slot.day][time_slot.shift]
    
    def clear(self):
        """Clear the time slot capacities and group time slots.
        """
        self.time_slot_capacities = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.group_time_slots = defaultdict(list)
        
        