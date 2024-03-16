from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
# Create your views here.

#serializer
from .serializer import SemesterSerializer, ParticipantSerializer, LaboratorySerializer, ModuleSerializer, ChapterSerialzer, GroupSerializer, AssistantSerializer, GroupMembershipSerializer

#viewset
from scheduling_data.models import Semester, Participant, Laboratory, Module, Chapter, Group, Assistant, GroupMembership

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    pagination_class = CustomPagination

    #post
    def create(self, request, *args, **kwargs):
        data = request.data
        name = data['name']
        status_semester = data['status'].capitalize()
        semester = Semester.objects.create(name=name, status=status_semester)
        serializer = self.get_serializer(semester)
        #if status_semester is true, then set other semester status to false
        if status_semester == 'True':
            #Get all semester with status true
            semesters = Semester.objects.filter(status=True)
            for sem in semesters:
                if sem.id != semester.id:
                    sem.status = False
                    sem.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=self.get_success_headers(serializer.data))
    
    #update
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        instance.name = data['name']
        instance.status = data['status'].capitalize()
        instance.save()

        #if status_semester is true, then set other semester status to false
        if instance.status == 'True':
            #Get all semester with status true
            semesters = Semester.objects.filter(status=True)
            for sem in semesters:
                if sem.id != instance.id:
                    sem.status = False
                    sem.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
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
    pagination_class = CustomPagination
    
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