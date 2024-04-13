# Author: Sazzad Hissain Khan
from django.shortcuts import render

# rest_framework
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

#mixin
from .mixin import ReadWriteSerializerMixin

#serializer
from .serializer import *

#viewset
from scheduling_data.models import Semester, Participant, Laboratory, Module, Chapter, Group, Assistant, GroupMembership
#filter
from scheduling_data.filters import *

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class SemesterViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    read_serializer_class = SemesterReadSerializer
    write_serializer_class = SemesterWriteSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SemesterFilter

    #retrieve
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        include_count = request.query_params.get('include_count', '')
        serializer = self.get_serializer(instance, context={'include_count': include_count, 'request': request})
        return Response(serializer.data)

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
    
    #get active semester
    def active(self, request, *args, **kwargs):
        include_count = request.query_params.get('include_count', '')
        active_semester = Semester.objects.filter(status=True)
        #count all child
        if active_semester.exists():
            active_semester = active_semester[0]
            serializer = self.get_serializer(active_semester, context={'include_count': include_count, 'request': request})
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        
        return Response(status=status.HTTP_404_NOT_FOUND, data={'message':'Semester aktif tidak ditemukan'})

    
class LaboratoryViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = Laboratory.objects.all()
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = LaboratoryFilter

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

class ModuleViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = Module.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ModuleFilter
    read_serializer_class = ModuleReadSerializer
    write_serializer_class = ModuleWriteSerializer

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
        # Check if module has child objects
        if instance.has_children():
            #return status 400 bad request and message
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message':'Modul masih terikat dengan chapter atau group'})
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message':'Failed to delete module'})
    
class ChapterViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ChapterFilter

    read_serializer_class = ChapterReadSerializer
    write_serializer_class = ChapterWriteSerializer
    
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = GroupFilter

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

class ParticipantViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ParticipantFilter
    read_serializer_class = ParticipantReadSerializer
    write_serializer_class = ParticipantWriteSerializer
    
    #update
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            updated_instance = serializer.save()
            updated_serializer = self.get_read_serializer_class()(updated_instance, context=self.get_serializer_context())
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': str(e)})
    
class AssistantViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):
    queryset = Assistant.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AssistantFilter
    read_serializer_class = AssistantReadSerializer
    write_serializer_class = AssistantWriteSerializer

    #update, update all data
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        try :
            updated_instance = serializer.save()
            updated_serializer = self.get_read_serializer_class()(updated_instance, context=self.get_serializer_context())
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': str(e)})

class GroupMembershipViewSet(viewsets.ModelViewSet):
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer