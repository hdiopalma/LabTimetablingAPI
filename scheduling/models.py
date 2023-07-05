from django.db import models

# Create your models here.
class Semester(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    
    def __str__(self) -> str:
        return self.name

class Laboratory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    
    def __str__(self) -> str:
        return self.name

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.name

class Participant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    nim = models.CharField(max_length=12)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    regular_schedule = models.JSONField()
    
    def __str__(self) -> str:
        return self.name

class Assistant(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    nim = models.CharField(max_length=12)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    regular_schedule = models.JSONField()
    prefered_schedule = models.JSONField()
    
    def __str__(self) -> str:
        return self.name

class Module(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    duration = models.DateTimeField(("dd-mm-YYYY"), auto_now=False, auto_now_add=False)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.name

class Chapter(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.name

class GroupMembership(models.Model):
    id = models.AutoField(primary_key=True)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f"Group Membership for Participant: {self.participant}, Group: {self.group}, Module: {self.module}, Laboratory: {self.laboratory}"