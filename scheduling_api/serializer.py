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
    laboratory = LaboratorySerializer()
    semester = SemesterSerializer()
    class Meta:
        model = Module
        id = serializers.ReadOnlyField()
        fields = ['url','name', 'start_date','end_date','laboratory','semester']
        
class ChapterSerialzer(serializers.HyperlinkedModelSerializer):
    module = ModuleSerializer()
    class Meta:
        model = Chapter
        id = serializers.ReadOnlyField()
        fields = ['url','name','module']
        
class GroupSerializer(serializers.HyperlinkedModelSerializer):
    module = ModuleSerializer()
    
    class Meta:
        model = Group
        id = serializers.ReadOnlyField()
        fields = ['url','name','module']
        
class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    semester = SemesterSerializer()
    class Meta:
        model = Participant
        id = serializers.ReadOnlyField()
        fields = ['url','name','nim','semester','regular_schedule']

class AssistantSerializer(serializers.HyperlinkedModelSerializer):
    laboratory = LaboratorySerializer()
    semester = SemesterSerializer()
    class Meta:
        model = Assistant
        id = serializers.ReadOnlyField()
        fields = ['url','name','nim','laboratory','semester','regular_schedule','prefered_schedule']
        
class GroupMembershipSerializer(serializers.HyperlinkedModelSerializer):
    participant = ParticipantSerializer()
    group = GroupMembership()
    class Meta:
        model = GroupMembership
        id = serializers.ReadOnlyField()
        fields = ['url','participant','group']