import copy
import numpy as np
from collections import defaultdict


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
                ("assistant", np.int32), 
                ("time_slot_date", np.float64),
                ("time_slot_day", 'U10'),  # 'U10' is a 10-character Unicode string
                ("time_slot_shift", 'U6')
            ])
        self._violations = defaultdict(dict)  # Using defaultdict to handle missing keys gracefully
        self.fitness = 0
        #grouped fitness, fitness_name: fitness_value
        self.grouped_fitness = defaultdict(float)

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
            (self._gene_data_list, other.gene_data)
        )
        new_chromosome.fitness = self.fitness + other.fitness

        # Merge violations
        new_chromosome._violations = defaultdict(dict)
        for src in (self._violations, other._violations):
            for key, value in src.items():
                new_chromosome._violations[key].update(value)

        # Merge grouped fitness
        new_chromosome.grouped_fitness = defaultdict(float)
        for src in (self.grouped_fitness, other.grouped_fitness):
            for key, value in src.items():
                new_chromosome.grouped_fitness[key] += value

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
        
    def add_violation(self, fitness_name: str, violation_data: dict):
        """        Adds a violation to the chromosome.
        Args:
            fitness_name (str): The name of the fitness function.
            violation_data (dict): A dictionary containing the violation data.
        """
        self._violations[fitness_name].update(violation_data)
        
    def get_violations(self) -> dict:
        """Returns the violations of the chromosome."""
        return copy.deepcopy(self._violations)
    
    def get_violation(self, fitness_name: str) -> dict:
        """Returns the violations of the chromosome for a specific fitness function."""
        return copy.deepcopy(self._violations.get(fitness_name, {}))
    
    def clear_violations(self):
        """Clears all violations of the chromosome."""
        self._violations.clear()
        
    def add_grouped_fitness(self, fitness_name: str, fitness_value: float):
        """Adds a grouped fitness value to the chromosome.
        Args:
            fitness_name (str): The name of the fitness function.
            fitness_value (float): The value of the fitness function.
        """
        self.grouped_fitness[fitness_name] += fitness_value
        
    def get_grouped_fitness(self) -> dict:
        """Returns the grouped fitness values of the chromosome."""
        return copy.deepcopy(self.grouped_fitness)
    
    def clear_grouped_fitness(self):
        """Clears all grouped fitness values of the chromosome."""
        self.grouped_fitness.clear()
        
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
