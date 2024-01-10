from scheduling_algorithm.data_parser import LaboratoryData, ModuleData, ChapterData, GroupData

class Gene:
    def __init__(self, laboratory: int, module: int, chapter: int, group: int):
        # Make sure that the data is immutable
        self._laboratory = laboratory
        self._module = module
        self._chapter = chapter
        self._group = group

    @property
    def laboratory(self):
        return self._laboratory
    
    @property
    def module(self):
        return self._module
    
    @property
    def chapter(self):
        return self._chapter
    
    @property
    def group(self):
        return self._group

    def __str__(self):
        return f"Gene(laboratory={self._laboratory}, module={self._module}, chapter={self._chapter}, group={self._group})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other: "Gene"):
        return self._laboratory == other.laboratory and self._module == other.module and self._chapter == other.chapter and self._group == other.group
    
    def __deepcopy__(self, memo):
        return self
    
    def __hash__(self):
        return hash((self._laboratory, self._module, self._chapter, self._group))
    
    @property
    def laboratory_data(self):
        return LaboratoryData.get_laboratory(self._laboratory)
    
    @property
    def module_data(self):
        return ModuleData.get_module(self._module)
    
    @property
    def chapter_data(self):
        return ChapterData.get_chapter(self._chapter)
    
    @property
    def group_data(self):
        return GroupData.get_group(self._group)
    
    @property
    def group_schedule(self):
        '''Returns the availability of the group'''
        return GroupData.get_schedule(self._group)