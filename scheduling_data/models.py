from django.db import models

# Create your models here.
class Semester(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=24)
    status = models.BooleanField(default=False)

    def children(self):
        return [laboratory for laboratory in self.laboratories.all()]
    
    def has_children(self):
        return self.laboratories.exists()
    
    def module_count(self):
        return sum([lab.module_count() for lab in self.laboratories.all()])
    
    def group_count(self):
        return sum([lab.group_count() for lab in self.laboratories.all()])
    
    def participant_count(self):
        return self.participants.count()
    
    def __str__(self) -> str:
        return self.name

class Laboratory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='laboratories')

    def has_module(self):
        return self.modules.exists()
    
    def has_assistant(self):
        return self.assistants.exists()
    
    def has_children(self):
        return self.has_module() or self.has_assistant()
    
    def module_count(self):
        return self.modules.count()
    
    def assistant_count(self):
        return self.assistants.count()
    
    def group_count(self):
        return sum([module.group_count() for module in self.modules.all()])
    
    def participant_count(self):
        return sum([module.participant_count() for module in self.modules.all()])
    
    def __str__(self) -> str:
        return self.name
    
class Module(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE, related_name='modules')

    def group_count(self):
        return self.groups.count()
    
    def participant_count(self):
        return sum([group.participant_count() for group in self.groups.all()])
    
    def chapter_count(self):
        return self.chapters.count()
    
    def __str__(self) -> str:
        return f"{self.name} - {self.laboratory.name} - {self.semester.name}"
        #return self.name

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

    def participant_count(self):
        return self.participants.count()
    
    def __str__(self) -> str:
        return self.name

class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    nim = models.CharField(max_length=12)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='participants')
    regular_schedule = models.JSONField() # {day: {shift: True/False}}
    groups = models.ManyToManyField(Group, through='GroupMembership', related_name='participants')
    
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
        return f"Group Membership for Participant: {self.participant}, Group: {self.group}"
    
class AssistantMembership(models.Model):
    id = models.AutoField(primary_key=True)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name="assistant_memberships")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="assistant_memberships")
    
    def __str__(self) -> str:
        return f"Assistant Membership for Assistant: {self.assistant}, Module: {self.module}, Laboratory: {self.laboratory}"

    