from django.db import models

# Create your models here.
class Semester(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=24)
    
    def __str__(self) -> str:
        return self.name

class Laboratory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    
    def __str__(self) -> str:
        return self.name
    
class Module(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='modules')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='modules')
    
    def __str__(self) -> str:
        return self.name

class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='chapters')
    
    def __str__(self) -> str:
        return self.name

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='groups')
    
    def __str__(self) -> str:
        return self.name

class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    nim = models.CharField(max_length=12)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='participants')
    regular_schedule = models.JSONField() 
    
    def __str__(self) -> str:
        return self.name

class Assistant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    nim = models.CharField(max_length=12)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='assistants')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='assistants')
    regular_schedule = models.JSONField()
    prefered_schedule = models.JSONField()
    
    def __str__(self) -> str:
        return self.name

class GroupMembership(models.Model):
    id = models.AutoField(primary_key=True)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name="group_memberships")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_memberships")
    
    def __str__(self) -> str:
        return f"Group Membership for Participant: {self.participant}, Group: {self.group}, Module: {self.module}, Laboratory: {self.laboratory}"
    
class AssistantMembership(models.Model):
    id = models.AutoField(primary_key=True)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name="assistant_memberships")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="assistant_memberships")
    
    def __str__(self) -> str:
        return f"Assistant Membership for Assistant: {self.assistant}, Module: {self.module}, Laboratory: {self.laboratory}"

    