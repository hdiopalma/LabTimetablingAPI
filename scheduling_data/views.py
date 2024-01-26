from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

#serializer
from .serializer import SemesterSerializer, ParticipantSerializer, LaboratorySerializer, ModuleSerializer, ChapterSerialzer, GroupSerializer, AssistantSerializer, GroupMembershipSerializer

#viewset
from scheduling_data.models import Semester, Participant, Laboratory, Module, Chapter, Group, Assistant, GroupMembership

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    
    
class LaboratoryViewSet(viewsets.ModelViewSet):
    queryset = Laboratory.objects.all()
    serializer_class = LaboratorySerializer

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    
class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerialzer
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        group_memberships = instance.group_memberships.all()
        group_memberships_data = [
            {
                'participant_name' : group_membership.participant.name,
                'participant_nim' : group_membership.participant.nim
            }
            for group_membership in group_memberships
        ]
        data['group_membership'] = group_memberships_data
        return Response(data)
    """

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    
    #update
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        instance.name = data['name']
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
class AssistantViewSet(viewsets.ModelViewSet):
    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer

class GroupMembershipViewSet(viewsets.ModelViewSet):
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer