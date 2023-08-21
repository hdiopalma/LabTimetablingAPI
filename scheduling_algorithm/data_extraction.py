from scheduling_data.models import *

class LaboratoryData:
    def get_laboratory(self):
        laboratory = Laboratory.objects.all()
        return laboratory
    
    def get_laboratory_assistant(self,id):
        laboratory = Laboratory.objects.filter(id=id).first()
        assistants = laboratory.assistants.all()
        assistants = [assistant for assistant in assistants]
        return assistants
    
    def get_laboratory_module(self,id):
        laboratory = Laboratory.objects.filter(id=id).first()
        modules = laboratory.modules.all()
        modules = [module for module in modules]
        return modules
    
class ModuleData:
    def get_module(self):
        modules = Module.objects.all()
        return modules

class ParticipantData:
    def get_participants(self):
        participants = Participant.objects.all()
        return participants
    
    def get_group(self, id):
        participant = Participant.objects.filter(id=id).first()
        group_memberships = participant.group_memberships.all()
        groups = []
        for group_membership in group_memberships:
            group = group_membership.group
            groups.append(group)
        return groups

class GroupData:
    def get_groups(self):
        groups = Group.objects.all()
        return groups
    
    def get_participants(self, id):
        group = Group.objects.filter(id=id).first()
        group_memberships = group.group_memberships.all()
        participants = []
        for group_membership in group_memberships:
            participant = group_membership.participant
            participants.append(participant)
        return participants
    
    def get_participant_schedule(self, id):
        participants = self.get_participants(id)
        participant_schedule = []
        for participant in participants:
            participant_schedule.append(participant.regular_schedule)
        return participant_schedule
    
    def get_group_schedule(self, id):
        participant_schedule = self.get_participant_schedule(id)
        days = participant_schedule[0].keys()
        merged_schedule = {day: {} for day in days}
        for day in days:
            for time_slot in participant_schedule[0][day]:
                is_available = all(schedule[day][time_slot] for schedule in participant_schedule)
                merged_schedule[day][time_slot] = is_available
        return merged_schedule
                
            
class AssistantData:
    def get_assistant(self):
        assistants = Assistant.objects.all()
        return assistants
    
    def get_assistant_modules(self,id):
        assistant = Assistant.object.filter(id=id).first()
        assistant_memberships = assistant.assistant_memberships.all()
        modules = []
        for assistant_membership in assistant_memberships:
            module = assistant_membership.module
            modules.append(module)
        return modules
    
