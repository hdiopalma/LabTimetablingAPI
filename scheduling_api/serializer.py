from rest_framework import serializers
from scheduling_data.models import Semester, Laboratory, Module, Chapter, Group, Participant, Assistant, GroupMembership

class SemesterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Semester
        id = serializers.ReadOnlyField()
        fields = ['url','name']
        
class LaboratorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Laboratory
        id = serializers.ReadOnlyField()
        fields = ['url','name']
        
class ModuleSerializer(serializers.HyperlinkedModelSerializer):
    #laboratory = LaboratorySerializer()
    #semester = SemesterSerializer()
    class Meta:
        model = Module
        id = serializers.ReadOnlyField()
        fields = ['url','name', 'start_date','end_date','laboratory','semester']
        
class ChapterSerialzer(serializers.HyperlinkedModelSerializer):
    #module = ModuleSerializer()
    class Meta:
        model = Chapter
        id = serializers.ReadOnlyField()
        fields = ['url','name','module']
        
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    #module = ModuleSerializer()
    participants = serializers.SerializerMethodField()
    
    def get_participants(self, instance):
        group_memberships = instance.group_memberships.all()
        participants = [gm.participant for gm in group_memberships]
        return ParticipantSerializer(participants, many=True, context=self.context).data
        
    class Meta:
        model = Group
        id = serializers.ReadOnlyField()
        fields = ['url','name','module','participants']
        
class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    #semester = SemesterSerializer()
    groups = serializers.SerializerMethodField()
    
    def get_groups(self, instance):
        group_memberships = instance.group_memberships.all()
        return GroupMembershipSerializer(group_memberships, many=True, context=self.context).data
    class Meta:
        model = Participant
        id = serializers.ReadOnlyField()
        fields = ['url','name','nim','semester','groups']

class AssistantSerializer(serializers.HyperlinkedModelSerializer):
    laboratory = LaboratorySerializer()
    semester = SemesterSerializer()
    class Meta:
        model = Assistant
        id = serializers.ReadOnlyField()
        fields = ['url','name','nim','laboratory','semester','regular_schedule','prefered_schedule']
        
class GroupMembershipSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GroupMembership
        id = serializers.ReadOnlyField()
        fields = ['url','participant','group']