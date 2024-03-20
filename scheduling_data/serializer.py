from rest_framework import serializers
from .models import Semester, Laboratory, Module, Chapter, Group, Participant, Assistant, GroupMembership

class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','status']

class LaboratoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        id = serializers.ReadOnlyField()
        fields = ['id','name','semester']

class LaboratoryReadSerializer(serializers.ModelSerializer):
    semester = SemesterSerializer()
    class Meta:
        model = Laboratory
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','semester']
        
class ModuleSerializer(serializers.ModelSerializer):
    laboratory = LaboratoryReadSerializer()
    semester = SemesterSerializer()
    class Meta:
        model = Module
        id = serializers.ReadOnlyField()
        fields = ['id','url','name', 'start_date','end_date','laboratory','semester']
        
class ChapterSerialzer(serializers.ModelSerializer):
    module = ModuleSerializer()
    class Meta:
        model = Chapter
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','module']
        
class GroupSerializer(serializers.ModelSerializer):
    #module = ModuleSerializer()
    participants = serializers.SerializerMethodField()
    regular_schedule = serializers.SerializerMethodField()
    module = ModuleSerializer()
    
    def get_participants(self, instance):
        group_memberships = instance.group_memberships.all()
        participants = [gm.participant for gm in group_memberships]
        #return ParticipantSerializer(participants, many=True, context=self.context).data
        participant_data = [{'id':p.id, 'name':p.name, 'nim':p.nim} for p in participants]
        return participant_data
        
    def get_regular_schedule(self, instance):
        group_memberships = instance.group_memberships.all()
        participants = [gm.participant for gm in group_memberships]
        schedules = [p.regular_schedule for p in participants]
        days = schedules[0].keys()
        merged_schedule = {day:{} for day in days}
        for day in days:
            for shift in schedules[0][day]:
                is_available = all([schedule[day][shift] for schedule in schedules])
                merged_schedule[day][shift] = is_available
        return merged_schedule

    class Meta:
        model = Group
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','module','participants','regular_schedule']
        
class ParticipantSerializer(serializers.ModelSerializer):
    #semester = SemesterSerializer()
    groups = serializers.SerializerMethodField()
    semester = SemesterSerializer()
    
    def get_groups(self, instance):
        group_memberships = instance.group_memberships.all()
        group_data = [{'id':gm.group.id, 'name':gm.group.name} for gm in group_memberships]
        return group_data
    class Meta:
        model = Participant
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','nim','semester','groups','regular_schedule']

class AssistantSerializer(serializers.ModelSerializer):
    laboratory = LaboratoryReadSerializer()
    semester = SemesterSerializer()

    class Meta:
        model = Assistant
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','nim','laboratory','semester','regular_schedule','prefered_schedule']
        
class GroupMembershipSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()
    class Meta:
        model = GroupMembership
        id = serializers.ReadOnlyField()
        fields = ['url','participant','group']