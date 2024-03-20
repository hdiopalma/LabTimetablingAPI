from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from .mixin import ReadWriteSerializerMixin
# Create your views here.

#serializer
from .serializer import *

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

        if instance.status:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message':'Semester aktif tidak dapat dihapus'})
        
        # Check if semester has child objects
        if instance.has_children():
            #return status 400 bad request and message
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message':'Semester masih terikat dengan laboratorium'})
        
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message':'Failed to delete semester'})
        
    #custom method
    #count semester
    def count(self, request, *args, **kwargs):
        semester_count = self.queryset.count()
        return Response({'semester_count':semester_count})
    
    #count module
    def count_module(self, request, *args, **kwargs):
        instance = self.get_object()
        module_count = instance.module_count()
        return Response({'module_count':module_count})
    
    #count group
    def count_group(self, request, *args, **kwargs):
        instance = self.get_object()
        group_count = instance.group_count()
        return Response({'group_count':group_count})
    
    #count participant
    def count_participant(self, request, *args, **kwargs):
        instance = self.get_object()
        participant_count = instance.participant_count()
        return Response({'participant_count':participant_count})
    
    #count all
    def count_all(self, request, *args, **kwargs):
        instance = self.get_object()
        module_count = instance.module_count()
        group_count = instance.group_count()
        participant_count = instance.participant_count()
        return Response({'module_count':module_count, 'group_count':group_count, 'participant_count':participant_count})
    
    
class LaboratoryViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = Laboratory.objects.all()
    pagination_class = CustomPagination

    read_serializer_class = LaboratoryReadSerializer
    write_serializer_class = LaboratoryWriteSerializer

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            updated_instance = serializer.save()
            updated_serializer = self.get_read_serializer_class()(updated_instance, context=self.get_serializer_context())
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': str(e)})
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if laboratory has child objects
        if instance.has_children():
            #return status 400 bad request and message
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message':'Laboratorium masih terikat dengan modul atau asisten'})
        
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message':'Failed to delete laboratory'})

    def count(self, request, *args, **kwargs):
        laboratory_count = self.queryset.count()
        return Response({'laboratory_count':laboratory_count})
    
    def count_module(self, request, *args, **kwargs):
        instance = self.get_object()
        module_count = instance.module_count()
        return Response({'module_count':module_count})
    
    def count_assistant(self, request, *args, **kwargs):
        instance = self.get_object()
        assistant_count = instance.assistant_count()
        return Response({'assistant_count':assistant_count})
    
    def count_group(self, request, *args, **kwargs):
        instance = self.get_object()
        group_count = instance.group_count()
        return Response({'group_count':group_count})
    
    def count_participant(self, request, *args, **kwargs):
        instance = self.get_object()
        participant_count = instance.participant_count()
        return Response({'participant_count':participant_count})
    
    def count_all(self, request, *args, **kwargs):
        instance = self.get_object()
        module_count = instance.module_count()
        assistant_count = instance.assistant_count()
        group_count = instance.group_count()
        participant_count = instance.participant_count()
        return Response({'module_count':module_count, 'assistant_count':assistant_count, 'group_count':group_count, 'participant_count':participant_count})

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