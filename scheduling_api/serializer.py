from rest_framework import serializers
from scheduling_data.models import Semester, Laboratory, Module, Chapter, Group, Participant, Assistant, GroupMembership

class SemesterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Semester
        id = serializers.ReadOnlyField()
        fields = ['url','name']
        
class ParticipantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Participant
        id = serializers.ReadOnlyField()
        fields = ['url','name','nim']

