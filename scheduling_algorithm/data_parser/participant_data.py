from scheduling_data.models import Participant
from functools import lru_cache

class ParticipantData:
        
    @classmethod
    @lru_cache(maxsize=10)
    def get_participants(cls):
        return Participant.objects.all()
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_participant(cls, id):
        return Participant.objects.get(id=id)
    
    @classmethod
    def get_random_participant(cls):
        return Participant.objects.order_by('?').first()
    
    @classmethod
    def get_groups(cls, id):
        participant = Participant.objects.get(id=id)
        if participant:
            groups_membership = participant.group_memberships.all()
            groups = []
            for group_membership in groups_membership:
                groups.append(group_membership.group)
            return groups
        return []
    
    @classmethod
    def get_modules(cls, id):
        participant = Participant.objects.get(id=id)
        if participant:
            groups_membership = participant.group_memberships.all()
            modules = []
            for group_membership in groups_membership:
                modules.append(group_membership.group.module)
            return modules
        return []
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_schedule(cls, id):
        participant = cls.get_participant(id)
        if participant:
            return participant.regular_schedule
        return None