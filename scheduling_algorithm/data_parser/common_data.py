from scheduling_algorithm.data_parser.assistant_data import AssistantData
from scheduling_algorithm.data_parser.group_data import GroupData
from functools import lru_cache
    
class CommonData:
    
    @classmethod
    @lru_cache(maxsize=256)
    def get_schedule(cls, id_assistant:int, id_group:int) -> dict:
        """Merges the schedule of the assistant and the group.

        Args:
            id_assistant (int): ID of the assistant.
            id_group (int): ID of the group.

        Returns:
            dict: The merged schedule.
        """
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