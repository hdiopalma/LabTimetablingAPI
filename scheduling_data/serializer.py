from rest_framework import serializers
from .models import *


def validate_schedule(value):
    default_structure = default_schedule()
    # Check if the incoming value have the same key (day) as the default structure
    if value.keys() != default_structure.keys():
        raise serializers.ValidationError("Invalid schedule structure, must be a dictionary with keys:"+str(default_structure.keys()))
    
    # Check if the value of each day have the same key (shift) as the default structure
    for day, shifts in value.items():
        if shifts.keys() != default_structure[day].keys():
            raise serializers.ValidationError("Invalid schedule structure, must be a dictionary with keys:"+str(default_structure[day].keys()))
        
        # Check if the value of each shift is a boolean
        for shift, availability in shifts.items():
            if not isinstance(availability, bool):
                raise serializers.ValidationError("Invalid schedule structure, must be a boolean value")

class SemesterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        id = serializers.ReadOnlyField()
        fields = ['id','name','status']

class SemesterReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','status']

    def to_representation(self, instance: Semester):
        data = super().to_representation(instance)
        include_count = self.context.get('include_count')
        count_method = {
            'laboratory': instance.laboratory_count,
            'module': instance.module_count,
            'group': instance.group_count,
            'participant': instance.participant_count,
            'assistant': instance.assistant_count,
            'all': lambda: {
                'laboratory': instance.laboratory_count(),
                'module': instance.module_count(),
                'group': instance.group_count(),
                'participant': instance.participant_count(),
                'assistant': instance.assistant_count(),
            }
        }
        if include_count and include_count in count_method:
            count_method = count_method[include_count]
            data['count'] = count_method() if callable(count_method) else count_method

        return data

class LaboratoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        id = serializers.ReadOnlyField()
        fields = ['id','name','semester']

    def to_representation(self, instance: Laboratory):
        data = super().to_representation(instance)
        if self.context.get('include_count', False):
            data['count'] = {
                'module': instance.module_count(),
                'group': instance.group_count(),
                'participant': instance.participant_count(),
                'assistant': instance.assistant_count(),
            }
        return data

class LaboratoryReadSerializer(serializers.ModelSerializer):
    semester = SemesterReadSerializer()
    class Meta:
        model = Laboratory
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','semester']
        

class ModuleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        id = serializers.ReadOnlyField()
        fields = ['id','name','start_date','end_date','laboratory']

class ModuleReadSerializer(serializers.ModelSerializer):
    laboratory = LaboratoryReadSerializer()
    class Meta:
        model = Module
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','start_date','end_date','laboratory']

class ChapterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        id = serializers.ReadOnlyField()
        fields = ['id','name','module']

class ChapterReadSerializer(serializers.ModelSerializer):
    module = ModuleReadSerializer()
    class Meta:
        model = Chapter
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','module']
        
class GroupSerializer(serializers.ModelSerializer):
    #module = ModuleSerializer()
    participants = serializers.SerializerMethodField()
    regular_schedule = serializers.SerializerMethodField()
    module = ModuleReadSerializer()
    
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

class ParticipantWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        id = serializers.ReadOnlyField()
        fields = ['id','name','nim','semester','regular_schedule','ipk']

    def validate_regular_schedule(self, value):
        validate_schedule(value)
        return value
    
    def is_valid(self, raise_exception=False):
        #Override is_valid method to validate schedule
        valid = super().is_valid(raise_exception=raise_exception)
        if not valid:
            return False #If the serializer is not valid, return False
        #If the serializer is valid, validate the schedule
        try:
            validate_schedule(self.validated_data['regular_schedule'])
        except serializers.ValidationError as e:
            self._errors['regular_schedule'] = e.detail
            return False
        return True
        

class ParticipantReadSerializer(serializers.ModelSerializer):
    #semester = SemesterSerializer()
    groups = serializers.SerializerMethodField()
    semester = SemesterReadSerializer()
    
    def get_groups(self, instance):
        group_memberships = instance.group_memberships.all()
        group_data = [{'id':gm.group.id, 'name':gm.group.name} for gm in group_memberships]
        return group_data
    class Meta:
        model = Participant
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','nim','semester','groups','regular_schedule', 'ipk']

class AssistantWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        id = serializers.ReadOnlyField()
        fields = ['id','name','nim','laboratory','semester','regular_schedule','prefered_schedule']

class AssistantReadSerializer(serializers.ModelSerializer):
    laboratory = LaboratoryReadSerializer()
    semester = SemesterReadSerializer()
    class Meta:
        model = Assistant
        id = serializers.ReadOnlyField()
        fields = ['id','url','name','nim','laboratory','semester','regular_schedule','prefered_schedule']

    def validate_regular_schedule(self, value):
        validate_schedule(value)
        return value
    
    def is_valid(self, raise_exception=False):
        #Override is_valid method to validate schedule
        valid = super().is_valid(raise_exception=raise_exception)
        if not valid:
            return False #If the serializer is not valid, return False
        #If the serializer is valid, validate the schedule
        try:
            validate_schedule(self.validated_data['regular_schedule'])
        except serializers.ValidationError as e:
            self._errors['regular_schedule'] = e.detail
            return False
        return True
        
class GroupMembershipSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    participant = serializers.SerializerMethodField()
    class Meta:
        model = GroupMembership
        id = serializers.ReadOnlyField()
        fields = ['url','participant','group']
        
class SolutionReadSerializer(serializers.ModelSerializer):
    semester = SemesterReadSerializer()
    class Meta:
        model = Solution
        id = serializers.ReadOnlyField()
        fields = ['id','name','semester','status','best_fitness','time_elapsed', 'gene_count']
        
class ScheduleDataReadSerializer(serializers.ModelSerializer):
    solution = serializers.SerializerMethodField()
    
    def get_solution(self, instance):
        return {
            'id': instance.solution.id,
            'name': instance.solution.name,
            'semester': instance.solution.semester.name
        }
    class Meta:
        model = ScheduleData
        id = serializers.ReadOnlyField()
        fields = ['id','solution','date','day','shift','assistant','group','laboratory','module','chapter']