from scheduling_data.models import Group
from functools import lru_cache

class GroupData:
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_groups(cls):
        # return Group.objects.all()
        return list(Group.objects.all())
    
    @classmethod
    @lru_cache(maxsize=100)
    def get_group(cls, id):
        return Group.objects.get(id=id)
    
    @classmethod
    def get_random_group(cls):
        return Group.objects.order_by('?').first()
    
    @classmethod
    def get_module(cls, id):
        group = cls.get_group(id)
        if group:
            return group.module
        return None
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_participants(cls, id):
        # group = cls.get_group(id)
        # return [m.participant for m in group.group_memberships.all()]
        group = Group.objects.prefetch_related('group_memberships__participant').get(id=id)
        return [m.participant for m in group.group_memberships.all()]
    
    @classmethod
    def get_assistants(cls, id):
        group = cls.get_group(id)
        if group:
            module = group.module
            assistants = []
            assistants_membership = module.assistant_memberships.all()
            for assistant_membership in assistants_membership:
                assistants.append(assistant_membership.assistant)
            return assistants
        return []
    
    @classmethod
    def get_participant_schedule(cls, id):
        participants = cls.get_participants(id)
        if participants:
            schedule = []
            for participant in participants:
                schedule.append(participant.regular_schedule)
            return schedule 
        return None
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_schedule(cls, id: int) -> dict:
        """Get the schedule of the group. The schedule is a dictionary with the days as keys and the shifts as values.

        Args:
            id (int): The id of the group.

        Returns:
            dict: The schedule of the group. If the group does not exist, return None.
            dict[day] (dict): The schedule of the group for the day.
            dict[day][shift] (bool): The availability of the group for the shift.
        """
        participants_schedule = cls.get_participant_schedule(id)
        if participants_schedule:
            days = participants_schedule[0].keys()
            merged_schedule = {day:{} for day in days}
            for day in days:
                for timeslot in participants_schedule[0][day]:
                    is_available = all([participant_schedule[day][timeslot] for participant_schedule in participants_schedule])
                    merged_schedule[day][timeslot] = is_available
            return merged_schedule
        return None
    