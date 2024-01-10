#import scheduling_data from LabTimetablingAPI/scheduling_data/models.py (2 levels up)
from scheduling_data.models import Laboratory
from functools import lru_cache

class LaboratoryData:

    @classmethod
    @lru_cache(maxsize=1)
    def get_laboratories(cls):
        return Laboratory.objects.all()
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_laboratory(cls, id):
        return Laboratory.objects.get(id=id)
    
    @classmethod
    def get_random_laboratory(cls):
        return Laboratory.objects.order_by('?').first()
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_assistants(cls, id):
        laboratory = cls.get_laboratory(id)
        if laboratory:
            return laboratory.assistants.all()
        return []