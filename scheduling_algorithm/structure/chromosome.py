import copy
#Simple data structure for timeslot
from collections import namedtuple
TimeSlot = namedtuple("TimeSlot", ["date", "day", "shift"])

class Chromosome:
    def __init__(self, genes: list = []):
        self._gene_data_list = [{"laboratory": gene["laboratory"], "module": gene["module"], "chapter": gene["chapter"], "group": gene["group"], "assistant": gene["assistant"], "time_slot": gene["time_slot"]} for gene in genes] if genes else []
        self.fitness = 0

    @property
    def gene_data(self):
        return self._gene_data_list
    
    def __str__(self):
        return f"Chromosome(length={len(self._gene_data_list)}, fitness={self.fitness})"
    
    def __repr__(self):
        return self.__str__()
    
    def __getitem__(self, index):
        return self._gene_data_list[index]

    def __len__(self):
        return len(self._gene_data_list)
    
    def __eq__(self, other: "Chromosome"):
        return self._gene_data_list == other.gene_data
    
    def __iter__(self):
        return iter(self._gene_data_list)
    
    #addition of chromosome
    def __add__(self, other: "Chromosome"):
        new_chromosome = Chromosome([])
        new_chromosome._gene_data_list = self._gene_data_list + other.gene_data
        new_chromosome.fitness = self.fitness + other.fitness
        return new_chromosome
    
    def transform_to_gene_data(self):
        return [self.to_gene_data(gene) for gene in self._gene_data_list]
    
    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        new_chromosome = Chromosome([])
        new_chromosome._gene_data_list = [copy.copy(gene_data) for gene_data in self._gene_data_list]
        new_chromosome.fitness = self.fitness
        memo[id(self)] = new_chromosome
        return new_chromosome
    
    def __hash__(self):
        return hash(tuple(self._gene_data_list))
    
    def copy(self):
        new_chromosome = Chromosome([])
        new_chromosome._gene_data_list = [gene_data.copy() for gene_data in self._gene_data_list]
        new_chromosome.fitness = self.fitness
        return new_chromosome

    def add_gene(self, laboratory: int, module: int, chapter: int, group: int, assistant: int = None, time_slot: TimeSlot = None):
        self._gene_data_list.append({"laboratory": laboratory, "module": module, "chapter": chapter, "group": group, "assistant": assistant, "time_slot": time_slot})

    def get_gene(self, index):
        return self._gene_data_list[index]
    
    def get_genes(self):
        return self._gene_data_list

    def set_assistant(self, index, assistant):
        self._gene_data_list[index]["assistant"] = assistant

    def set_time_slot(self, index, time_slot):
        self._gene_data_list[index]["time_slot"] = time_slot

    def to_json(self):
        return {"gene_data": self._gene_data_list, "fitness": self.fitness}