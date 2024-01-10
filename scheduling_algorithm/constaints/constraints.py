from scheduling_algorithm.data_parser import LaboratoryData, ModuleData, ChapterData, GroupData, AssistantData

class BaseConstraint:
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Constraint(name={self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, gene: dict):
        raise NotImplementedError("Constraint function not implemented")
    
# Ensure that each chapter is assigned to the correct module.
class ChapterModuleConstraint(BaseConstraint):
    def __init__(self):
        super().__init__("ChapterModuleConstraint")
        self.chapters = ChapterData

    def __call__(self, gene: dict):
        if gene["module"] == self.chapters.get_module(gene["module"]).id:
            return True
        return False
    
# Ensure that each group is assigned to the correct module.
class GroupModuleConstraint(BaseConstraint):
    def __init__(self):
        super().__init__("GroupModuleConstraint")
        self.groups = GroupData
    
    def __call__(self, gene: dict):
        if gene["module"] == self.groups.get_module(gene["module"]).id:
            return True
        return False
    
# Ensure that each module is assigned to the correct lab.
class ModuleLaboratoryConstraint(BaseConstraint):
    def __init__(self):
        super().__init__("ModuleLaboratoryConstraint")
        self.modules = ModuleData
    
    def __call__(self, gene: dict):
        if gene["laboratory"] == self.modules.get_laboratory(gene["module"]).id:
            return True
        return False
    
# Ensure that each assistant is assigned to the correct lab.
class AssistantLaboratoryConstraint(BaseConstraint):
    def __init__(self):
        super().__init__("AssistantLaboratoryConstraint")
        self.assistants = AssistantData
    
    def __call__(self, gene: dict):
        if gene["laboratory"] == self.assistants.get_laboratory(gene["assistant"]).id:
            return True
        return False
    
# Ensure that the group schedule is not violated by the gene time slot.
class ScheduleConstraint(BaseConstraint):
    def __init__(self):
        super().__init__("ScheduleConstraint")
        self.groups = GroupData
    
    def __call__(self, gene: dict):
        schedule = self.groups.get_schedule(gene["group"])
        if schedule:
            return schedule[gene["time_slot"].day][gene["time_slot"].shift]
        return False
    
# Ensure that the assistant schedule is not violated by the gene time slot.
class AssistantScheduleConstraint(BaseConstraint):
    def __init__(self):
        super().__init__("AssistantScheduleConstraint")
        self.assistants = AssistantData
    
    def __call__(self, gene: dict):
        schedule = self.assistants.get_schedule(gene["assistant"])
        if schedule:
            return schedule[gene["time_slot"].day][gene["time_slot"].shift]
        return False
    
# Ensure that the group schedule and assistant schedule is not violated each other
class GroupAssistantScheduleConstraint(BaseConstraint):
    def __init__(self):
        super().__init__("GroupAssistantScheduleConstraint")
        self.groups = GroupData
        self.assistants = AssistantData
    
    def __call__(self, gene: dict):
        '''Returns true if the group schedule and assistant schedule is not violated each other'''
        group_schedule = self.groups.get_schedule(gene["group"])
        assistant_schedule = self.assistants.get_schedule(gene["assistant"])
        if group_schedule and assistant_schedule:
            return group_schedule[gene["time_slot"].day][gene["time_slot"].shift] and assistant_schedule[gene["time_slot"].day][gene["time_slot"].shift]
        return False
    
# Dynamic Constraint Class (custom constraint function) for on demand constraint
class DynamicConstraint(BaseConstraint):
    def __init__(self, name, constraint_function):
        super().__init__(name)
        self.constraint_function = constraint_function
    
    def __call__(self, gene: dict):
        return self.constraint_function(gene)
    
# Wrapper class for constraint
from typing import List
class ConstraintManager:
    def __init__(self, constraints: List[BaseConstraint]):
        self.constraints = constraints
    
    def __str__(self):
        return f"Constraint(constraints={self.constraints})"
    
    def __repr__(self):
        return self.__str__()
    
    def __call__(self, gene: dict):
        return all([constraint(gene) for constraint in self.constraints])