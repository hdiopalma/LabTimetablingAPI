
from collections import defaultdict, namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"]) #Simple data structure for timeslot, for reference

from scheduling_algorithm.data_parser import Constant
from scheduling_algorithm.data_parser import ModuleData, GroupData

import random
from datetime import timedelta, datetime
from math import floor


class TimeSlotManager:
    """
    Class to manage time slot generation and manipulation, 
    such as to prioritize the slot up to a certain capacity
    before moving to the next slot. Track the slot capacity
    and the slot that has been used. Also track the slot data. 
    Each module have a different slot capacity.
    For example, a Electrical Engineering module have a slot capacity of 3 groups per slot, 
    while a Mechanical Engineering module have a slot capacity of 2 groups per slot.
    Different module that from different department can have the same slot, because they are not using the same laboratory.
    But the one that have the same module or laboratory cannot have the same slot after a certain capacity.
    This will make sure the slot is not too sparse, and the slot is not too dense so that the assistant can handle the group effectively.
    
    Will be used in the factory class and the scheduling algorithm class (Genetic Algorithm).
    
    The tracked timeslot consists of the date, day, and shift. It also with module and lab id to track the capacity.
    
    """
    def __init__(self):
        self.time_slot_capacity = {}
        self.capacity_data = {}
        
    def add_capacity(self, lab_id, module_id, capacity):
        """
        Add capacity data for a laboratory and module.
        
        Args:
            lab_id (int): The laboratory id.
            module_id (int): The module id.
            capacity (int): The capacity for the laboratory and module.
        """
        self.capacity_data.add((lab_id, module_id, capacity))
        
    def generate_empty_time_slot(self, start_date: datetime, end_date: datetime, module_id: int, capacity: int):
        """
        Generate the initial empty time slot based on the start date, end date, lab id, and module id.
        
        Args:
            start_date (datetime): The start date of the schedule.
            end_date (datetime): The end date of the schedule.
            lab_id (int): The laboratory id.
            module_id (int): The module id.
            
        Returns:
            dict: The empty time slot for the laboratory and module. structure: {timeslot: (lab_id, module_id): capacity}
        """
        
        #if start_date not start from Monday, then start from the next Monday
        if start_date.weekday() != 0:
            start_date = start_date + timedelta(days=7 - start_date.weekday())
        duration = (end_date - start_date).days + 1
        weeks_duration = floor(duration / 7)
        #iterate through the duration to generate the empty time slot
        for week in range(weeks_duration):
            for day in Constant.days:
                for shift in Constant.shifts:
                    date = (start_date + timedelta(days=week * 7 + Constant.days.index(day))).date().isoformat().replace("-", "")
                    timeslot = TimeSlot(date, day, shift)
                    if module_id not in self.time_slot_capacity:
                        self.time_slot_capacity[module_id] = {}
                    self.time_slot_capacity[module_id][timeslot] = {"max_capacity": capacity, "capacity": 0, "groups": []}
        self.capacity_data[module_id] = capacity
        #shuffle the time slot capacity
        return self.time_slot_capacity
    
    def add_group_to_time_slot(self, timeslot: TimeSlot, module_id: int, group_id: int):
        """
        Add a group to the time slot based on the module.
        
        Args:
            timeslot (TimeSlot): The time slot to add the group.
            module_id (int): The module id.
            group_id (int): The group id.
        """
        # 
        if group_id in self.time_slot_capacity[module_id][timeslot]["groups"]:
            return False
        self.time_slot_capacity[module_id][timeslot]["capacity"] += 1
        self.time_slot_capacity[module_id][timeslot]["groups"].append(group_id)
        return True
    
    def generate_available_time_slot(self, module_id: int, group_id: int, randomize: bool = False) -> TimeSlot:
        """Generate an available time slot for a group based on the module, lab, and group id.
        The generated time slot is based on the availability of the group and the capacity of empty time slot of the lab and module.

        Args:
            module_id (int): The module id.
            group_id (int): The group id.
            randomize (bool): The flag to randomize the time slot iteration.

        Raises:
            ValueError: An error occurred if the empty time slot has not been generated for the lab and module.

        Returns:
            TimeSlot: The available time slot for the group. If the time slot is not available, return a random time slot.
        """
        
        if  module_id not in self.capacity_data:
            print(f"Module id: {module_id} not in capacity data.")
            print("Please add the capacity data for the module using generate_empty_time_slot method.")
            raise ValueError("The empty time slot has not been generated for the module, please generate the empty time slot first using generate_empty_time_slot method.")
        
        if randomize:
            return self.randomize_generate_available_time_slot(module_id, group_id)
        else:
            return self.iteratively_generate_available_time_slot(module_id, group_id)
    
    def iteratively_generate_available_time_slot(self, module_id: int, group_id: int) -> TimeSlot:
        module_date = ModuleData.get_dates(module_id)
        group_schedule = GroupData.get_schedule(group_id)
        for timeslot, data in self.time_slot_capacity[module_id].items():
            if data["capacity"] < data["max_capacity"] and group_schedule[timeslot.day][timeslot.shift]:
                if self.add_group_to_time_slot(timeslot, module_id, group_id):
                    return timeslot
        print(f"No available time slot for group id: {group_id}, generate random time slot.")
        return self.generate_random_time_slot(module_date.start_date, module_date.end_date)
    
    def randomize_generate_available_time_slot(self, module_id: int, group_id: int) -> TimeSlot:
        module_date = ModuleData.get_dates(module_id)
        group_schedule = GroupData.get_schedule(group_id)
        
        selected_time_slot = self.select_time_slot_based_on_capacity(module_id, group_schedule)
        if selected_time_slot:
            for timeslot in selected_time_slot:
                if self.add_group_to_time_slot(timeslot, module_id, group_id):
                    return timeslot
        print(f"No available time slot for group id: {group_id}, generate random time slot.")
        return self.generate_random_time_slot(module_date.start_date, module_date.end_date)
    
    def select_time_slot_based_on_capacity(self, module_id: int, group_schedule: dict) -> list:
        weight_time_slot = self.calculate_weighted_time_slot(module_id, group_schedule)
        if weight_time_slot:
            #Select at most 10 time slot based on the weight, to reduce the chance of the group being assigned to the same slot
            time_slot = random.choices(list(weight_time_slot.keys()), weights=weight_time_slot.values(), k=10)
            return time_slot
        print(f"Weighted time slot is empty for module id: {module_id}.")
        return None
    
    def calculate_weighted_time_slot(self, module_id: int, group_schedule: dict) -> dict:
        weight_time_slot = {}
        for timeslot, data in self.time_slot_capacity[module_id].items():
            if data["capacity"] < data["max_capacity"] and group_schedule[timeslot.day][timeslot.shift]:
                # calculate the weight based on the capacity, the closer to the max capacity, the higher the weight
                weight = 1.0 / (data["max_capacity"] - data["capacity"])
                if data["capacity"] == 0:
                    # Reduce the weight if the capacity is 0, to lessen the chance of the slot being selected, don't wanna the group feels lonely
                    weight = weight / data["max_capacity"]
                weight_time_slot[timeslot] = weight
        return weight_time_slot
        
    
    @staticmethod
    def generate_random_time_slot(start_date: datetime, end_date: datetime) -> TimeSlot:
        """
        Generate a random time slot based on the start date and end date.
        
        Args:
            start_date (datetime): The start date of the schedule.
            end_date (datetime): The end date of the schedule.
            
        Returns:
            TimeSlot: The random time slot.
        """
        
        if type(start_date) is not datetime or type(end_date) is not datetime:
            raise ValueError("The start date and end date must be in datetime format.")
        
        #if start_date not start from Monday, then start from the next Monday
        if start_date.weekday() != 0:
            start_date = start_date + timedelta(days=7 - start_date.weekday())
        duration = (end_date - start_date).days + 1
        random_date = start_date + timedelta(days=random.randint(0, duration - 1))
        while random_date.weekday() == 6:  # Sunday is 6 in Python's weekday() function, if the random date is Sunday, then generate another random date
            random_date = start_date + timedelta(days=random.randint(0, duration - 1))
        random_days = Constant.days[random_date.weekday()]
        random_shifts = random.choice(Constant.shifts)
        return TimeSlot(random_date, random_days, random_shifts)
        
    def to_dict(self):
        """Convert the time slot data to json format."""
        json_data = {}
        for module_id, data in self.time_slot_capacity.items():
            for timeslot, capacity_data in data.items():
                time_slot_data = {
                    "capacity": capacity_data["capacity"],
                    "max_capacity": capacity_data["max_capacity"],
                    "groups": capacity_data["groups"],
                    "module_id": module_id
                }
                time_slot_detail = {
                    "date": timeslot.date,
                    "day": timeslot.day,
                    "shift": timeslot.shift,
                    "data": time_slot_data
                }
                if timeslot.date not in json_data:
                    json_data[timeslot.date] = []
                json_data[timeslot.date].append(time_slot_detail)
        return json_data
        
        