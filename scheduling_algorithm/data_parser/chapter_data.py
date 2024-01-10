from scheduling_data.models import Chapter
from functools import lru_cache

class ChapterData:
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_chapters(cls):
        return Chapter.objects.all()
    
    @classmethod
    @lru_cache(maxsize=None)
    def get_chapter(cls, id):
        return Chapter.objects.get(id=id)
    
    @classmethod
    def get_module(cls, id):
        chapter = cls.get_chapter(id)
        if chapter:
            return chapter.module
        return None
    
    @classmethod
    def get_random_chapter(cls, id):
        chapter = Chapter.objects.get(id=id)
        if chapter:
            return chapter.module
        return None