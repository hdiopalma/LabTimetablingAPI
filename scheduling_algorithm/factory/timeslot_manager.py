from collections import namedtuple
from datetime import timedelta, datetime
from math import floor
from functools import lru_cache
from scheduling_algorithm.data_parser import Constant, ModuleData


# Define the TimeSlot namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])

class TimeSlotManager:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self._generate_all_time_slots()

    def _generate_all_time_slots(self):
        self.all_time_slots = []
        weeks_duration = max(1, floor(((self.end_date - self.start_date).days + 1) / 7))
        for week in range(weeks_duration):
            for day in Constant.days:
                for shift in Constant.shifts:
                    date = (self.start_date + timedelta(days=week * 7 + Constant.days.index(day))).timestamp()
                    timeslot = TimeSlot(date, day, shift)
                    self.all_time_slots.append(timeslot)
        
        self.time_slot_to_index = {ts: i for i, ts in enumerate(self.all_time_slots)}
        self.index_to_time_slot = {i: ts for i, ts in enumerate(self.all_time_slots)}

    def set_start_date(self, new_start_date):
        self.start_date = new_start_date
        self._generate_all_time_slots()

    def set_end_date(self, new_end_date):
        self.end_date = new_end_date
        self._generate_all_time_slots()

    def set_date_range(self, new_start_date, new_end_date):
        self.start_date = new_start_date
        self.end_date = new_end_date
        self._generate_all_time_slots()

# Singleton instance of TimeSlotManager (for global access)
time_slot_manager = TimeSlotManager(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
)

# Accessor functions
def get_all_time_slots():
    return time_slot_manager.all_time_slots

def get_time_slot_by_index(index):
    return time_slot_manager.index_to_time_slot.get(index)

def get_index_by_time_slot(time_slot):
    return time_slot_manager.time_slot_to_index.get(time_slot)

def set_start_date(new_start_date):
    time_slot_manager.set_start_date(new_start_date)

def set_end_date(new_end_date):
    time_slot_manager.set_end_date(new_end_date)

def set_date_range(new_start_date, new_end_date):
    time_slot_manager.set_date_range(new_start_date, new_end_date)
    
@lru_cache(maxsize=24)
def get_date_range(module_id:int, week:int = 0) -> tuple:
    """Returns the date range based on the module and the current week index.

    Args:
        module_id (int): The module ID.
        week (int): The week index.

    Returns:
        tuple: The date range.
    """
    start_date = ModuleData.get_dates(module_id).start_date
    if week > 0:
        start_date += timedelta(weeks=week - 1)
        end_date = start_date + timedelta(weeks=1)
    else:
        end_date = ModuleData.get_dates(module_id).end_date
    return start_date, end_date