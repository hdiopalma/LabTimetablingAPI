from scheduling_data.models import Assistant
from functools import lru_cache

class AssistantData:
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_assistants(cls):
        return Assistant.objects.all()
    
    @classmethod
    def get_assistant(cls, id):
        return Assistant.objects.get(id=id)
    
    @classmethod
    def get_random_assistant(cls):
        # This is for testing purposes only
        return Assistant.objects.order_by('?').first()
    
    @classmethod
    def get_laboratory(cls, id):
        assistant = Assistant.objects.get(id=id)
        if assistant:
            return assistant.laboratory
        return None
    
    @classmethod
    def get_modules(cls, id):
        assistant = Assistant.objects.get(id=id)
        if assistant:
            modules = []
            assistant_membership = assistant.assistant_memberships.all()
            for assistant_membership in assistant_membership:
                modules.append(assistant_membership.module)
            return modules
        return []
    
    @classmethod
    def get_groups(cls, id):
        assistant = Assistant.objects.get(id=id)
        if assistant:
            modules = cls.get_modules(id)
            groups = []
            for module in modules:
                groups.append(module.groups.all())
            return groups
        return []
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_schedule(cls, id):
        assistant = Assistant.objects.get(id=id)
        if assistant:
            return assistant.regular_schedule
        return None