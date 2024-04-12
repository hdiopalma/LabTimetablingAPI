import django_filters
from scheduling_data.models import *

class SemesterFilter(django_filters.FilterSet):
    '''Filter for Semester model'''
    status = django_filters.BooleanFilter(field_name='status')
    class Meta:
        model = Semester
        fields = ['name', 'status']

class LaboratoryFilter(django_filters.FilterSet):
    '''Filter for Laboratory model'''
    semester_id = django_filters.NumberFilter(field_name='semester_id')
    class Meta:
        model = Laboratory
        fields = ['name', 'semester_id']

class ModuleFilter(django_filters.FilterSet):
    '''Filter for Module model'''
    semester_id = django_filters.NumberFilter(field_name='laboratory__semester_id')
    laboratory_id = django_filters.NumberFilter(field_name='laboratory_id')
    class Meta:
        model = Module
        fields = ['name', 'semester_id', 'laboratory_id']

class ChapterFilter(django_filters.FilterSet):
    '''Filter for Chapter model'''
    module_id = django_filters.NumberFilter(field_name='module_id')
    laboratory_id = django_filters.NumberFilter(field_name='module__laboratory_id')
    semester_id = django_filters.NumberFilter(field_name='module__laboratory__semester_id')
    class Meta:
        model = Chapter
        fields = ['name', 'module_id', 'laboratory_id', 'semester_id']

class GroupFilter(django_filters.FilterSet):
    '''Filter for Group model'''
    module_id = django_filters.NumberFilter(field_name='module_id')
    laboratory_id = django_filters.NumberFilter(field_name='module__laboratory_id')
    semester_id = django_filters.NumberFilter(field_name='module__laboratory__semester_id')
    class Meta:
        model = Group
        fields = ['name', 'module_id', 'laboratory_id', 'semester_id']

class AssistantFilter(django_filters.FilterSet):
    '''Filter for Assistant model'''
    laboratory_id = django_filters.NumberFilter(field_name='laboratory_id')
    semester_id = django_filters.NumberFilter(field_name='semester_id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    nim = django_filters.CharFilter(field_name='nim', lookup_expr='icontains')
    class Meta:
        model = Assistant
        fields = ['name', 'nim', 'laboratory_id', 'semester_id']

class ParticipantFilter(django_filters.FilterSet):
    '''Filter for Participant model'''
    semester_id = django_filters.NumberFilter(field_name='semester_id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    nim = django_filters.CharFilter(field_name='nim', lookup_expr='icontains')
    group_id = django_filters.NumberFilter(field_name='groups__id')
    #ipk range filter
    ipk_min = django_filters.NumberFilter(field_name='ipk', lookup_expr='gte')
    ipk_max = django_filters.NumberFilter(field_name='ipk', lookup_expr='lte')
    class Meta:
        model = Participant
        fields = ['name', 'nim', 'semester_id', 'group_id', 'ipk_min', 'ipk_max']

