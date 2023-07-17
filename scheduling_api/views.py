from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.

#serializer
from .serializer import SemesterSerializer, ParticipantSerializer

#viewset
from scheduling_data.models import Semester, Participant

class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        group_memberships = instance.group_memberships.all()
        group_membership_data = [
            {
                'group_name':group_membership.group.name,
                'module_name': group_membership.group.module.name
             } 
            for group_membership in group_memberships
            ]
        
        data['group_membership'] = group_membership_data
        return Response(data)
