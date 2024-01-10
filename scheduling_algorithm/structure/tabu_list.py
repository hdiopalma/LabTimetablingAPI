from collections import deque
from scheduling_algorithm.structure import Chromosome

class TabuList:
    def __init__(self, tabu_list_size: int = 10):
        self.tabu_list_size = tabu_list_size
        self.tabu_list = deque(maxlen=tabu_list_size)
    
    def __str__(self):
        return f"TabuList(tabu_list_size={self.tabu_list_size}, tabu_list={self.tabu_list})"
    
    def __contains__(self, chromosome: Chromosome):
        return chromosome in self.tabu_list
    
    def __len__(self):
        return len(self.tabu_list)
    
    def __getitem__(self, index):
        return self.tabu_list[index]
    
    def __setitem__(self, index, chromosome: Chromosome):
        self.tabu_list[index] = chromosome
    
    def __delitem__(self, index):
        del self.tabu_list[index]
    
    def __iter__(self):
        return iter(self.tabu_list)
    
    def __reversed__(self):
        return reversed(self.tabu_list)
    
    def __add__(self, chromosome: Chromosome):
        self.tabu_list.append(chromosome)
    
    # def is_tabu(self, chromosome: Chromosome) -> bool:
    #     return chromosome in self.tabu_list
    
    def configure(self, tabu_list_size: int):
        self.tabu_list_size = tabu_list_size
        self.tabu_list = deque(maxlen=tabu_list_size)
        return self