from assistant_data import AssistantData
from group_data import GroupData

from collections import namedtuple
ModuleDate = namedtuple('ModuleDate', ['start_date', 'end_date'])
    
class CommonData:
    
    @classmethod
    def get_available_schedule(cls, id_assistant, id_group):
        assistants_schedule = AssistantData.get_schedule(id_assistant)
        groups_schedule = GroupData.get_schedule(id_group)
        if assistants_schedule and groups_schedule:
            days = assistants_schedule.keys()
            merged_schedule = {day:{} for day in days}
            for day in days:
                for timeslot in assistants_schedule[day]:
                    is_available = assistants_schedule[day][timeslot] & groups_schedule[day][timeslot]
                    merged_schedule[day][timeslot] = is_available
            return merged_schedule