import copy
import numpy as np


class Chromosome:

    def __init__(self, genes: list = []):
        # data = [{"laboratory": gene["laboratory"], "module": gene["module"], "chapter": gene["chapter"], "group": gene["group"], "assistant": gene["assistant"], "time_slot": gene["time_slot"]} for gene in genes] if genes else []
        data = [(gene["laboratory"], gene["module"], gene["chapter"],
                 gene["group"], gene["assistant"], gene["time_slot"][0], gene["time_slot"][1], gene["time_slot"][2])
                for gene in genes] if genes else []
        self._gene_data_list = np.array(
            data,
            dtype=[
                ("laboratory", np.int32),
                ("module", np.int32),
                ("chapter", np.int32),
                ("group", np.int32),
                ("assistant", np.int32),  # Assuming assistant IDs are integers
                ("time_slot_date", np.float64),
                ("time_slot_day", 'U10'),  # 'U10' is a 10-character Unicode string
                ("time_slot_shift", 'U6')
            ])
        self._violations = {}  # for storing violations
        self.fitness = 0

        #week number, used for tracking the week number of the chromosome when using the weekly based algorithm
        self.week = 0

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
        return np.array_equal(self._gene_data_list, other.gene_data)

    def __iter__(self):
        return iter(self._gene_data_list)

    #addition of chromosome
    def __add__(self, other: "Chromosome"):
        new_chromosome = Chromosome([])
        new_chromosome._gene_data_list = np.concatenate(
            (self._gene_data_list, other.gene_data))
        new_chromosome.fitness = self.fitness + other.fitness
        return new_chromosome

    def transform_to_gene_data(self):
        return [self.to_gene_data(gene) for gene in self._gene_data_list]

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        new_chromosome = Chromosome([])
        new_chromosome._gene_data_list = np.copy(self._gene_data_list)
        new_chromosome.fitness = self.fitness
        new_chromosome.week = self.week
        memo[id(self)] = new_chromosome
        return new_chromosome

    def __hash__(self):
        return hash(self._gene_data_list.tobytes())

    def copy(self):
        new_chromosome = Chromosome([])
        new_chromosome._gene_data_list = np.copy(self._gene_data_list)
        new_chromosome.fitness = self.fitness
        new_chromosome.week = self.week
        return new_chromosome

    def add_gene(self,
                 laboratory: int,
                 module: int,
                 chapter: int,
                 group: int,
                 assistant: int = None,
                 time_slot: tuple = None):
        self._gene_data_list = np.append(
            self._gene_data_list,
            np.array(
                [(laboratory, module, chapter, group, assistant, time_slot[0], time_slot[1], time_slot[2])],
                dtype=self._gene_data_list.dtype))
        # self._gene_data_list.append({"laboratory": laboratory, "module": module, "chapter": chapter, "group": group, "assistant": assistant, "time_slot": time_slot})

    def get_gene(self, index):
        return self._gene_data_list[index]

    def get_genes(self):
        return self._gene_data_list

    def set_assistant(self, index, assistant):
        self._gene_data_list["assistant"][index] = assistant

    def set_time_slot(self, index, time_slot):
        self._gene_data_list["time_slot_date"][index] = time_slot[0]
        self._gene_data_list["time_slot_day"][index] = time_slot[1]
        self._gene_data_list["time_slot_shift"][index] = time_slot[2]

    def set_week(self, week: int):
        self.week = week
        
    def add_violation(self, constraint_name: str, penalty: float):
        self._violations[constraint_name] = self._violations.get(constraint_name, 0.0) + penalty
    
    def get_violations(self):
        return self._violations.copy()
    
    def reset_violations(self):
        self._violations.clear()

    def to_json(self):
        genes = []
        for gene in self._gene_data_list:
            genes.append({
                "laboratory": gene["laboratory"],
                "module": gene["module"],
                "chapter": gene["chapter"],
                "group": gene["group"],
                "assistant": gene["assistant"],
                "time_slot": (gene["time_slot_date"], gene["time_slot_day"], gene["time_slot_shift"])
            })
        return {"genes": genes, "fitness": self.fitness}
