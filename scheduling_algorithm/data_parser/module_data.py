from scheduling_data.models import Module
from functools import lru_cache

from collections import namedtuple
ModuleDate = namedtuple('ModuleDate', ['start_date', 'end_date'])

class ModuleData:
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_modules(cls):
        return Module.objects.all()
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_module(cls, id: int) -> Module:
        """Get a module by id, the result is cached.

        Args:
            id (int): The id of the module.

        Returns:
            Module: The module with the given id.
        """
        return Module.objects.get(id=id)
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_dates(cls, id: int) -> ModuleDate:
        """Get the start date and end date of a module by id.

        Args:
            id (int): The id of the module.

        Returns:
            ModuleDate: The start date and end date of the module. If the module does not exist, return None.
            ModuleDate.start_date (datetime): The start date of the module.
            ModuleDate.end_date (datetime): The end date of the module.
        """
        module = cls.get_module(id)
        if module:
            return ModuleDate(module.start_date, module.end_date)
        return None

    
    @classmethod
    def get_random_module(cls):
        return Module.objects.order_by('?').first()
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_laboratory(cls, id):
        module = cls.get_module(id)
        if module:
            return module.laboratory
        return None
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_groups(cls, id):
        module = cls.get_module(id)
        if module:
            return module.groups.all()
        return []
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_chapters(cls, id):
        module = cls.get_module(id)
        if module:
            return module.chapters.all()
        return []
    
    @classmethod
    def get_participants(cls, id):
        module = cls.get_module(id)
        if module:
            groups = module.groups.all()
            participants = []
            for group in groups:
                group_memberships = group.group_memberships.all()
                for group_membership in group_memberships:
                    participants.append(group_membership.participant)
            return participants
        return []
    
    @classmethod
    def get_assistants(cls, id):
        module = cls.get_module(id)
        if module:
            assistants = []
            assistants_membership = module.assistant_memberships.all()
            for assistant_membership in assistants_membership:
                assistants.append(assistant_membership.assistant)
            return assistants
        return []