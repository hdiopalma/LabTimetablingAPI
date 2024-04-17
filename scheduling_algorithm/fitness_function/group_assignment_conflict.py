#GroupAssignmentConflictPenalty
from collections import defaultdict
from scheduling_algorithm.structure.chromosome import Chromosome
from scheduling_algorithm.fitness_function.base_fitness import BaseFitness

class GroupAssignmentConflictFitness(BaseFitness):
    """Count the number of groups assigned to a time slot in a lab, and penalize the chromosome if the number of groups exceeds the maximum threshold"""
    def __init__(self):
        super().__init__("GroupAssignmentConflictFitness")
        self.max_threshold = 3 # Maximum number of groups that can be assigned to a single time slot in lab
        self.conflict_penalty = 1 # Penalty for each group that exceeds the maximum threshold
        
        #conflicts[laboratory][module][time_slot] = [groups]
        self._conflicts = self.default_outer_dict()
        # Keeps track of the number of groups assigned to a time slot in a lab, initialized to 0

    def default_inner_dict(self):
        return defaultdict(list)
    
    def default_middle_dict(self):
        return defaultdict(self.default_inner_dict)
    
    def default_outer_dict(self):
        return defaultdict(self.default_middle_dict)

    def __call__(self, chromosome: Chromosome):
        self._conflicts.clear()
        for gene in chromosome:
            #gene = chromosome.to_gene_data(gene)
            #self._conflicts[gene.laboratory][gene.module][gene.time_slot].append(gene.group)
            #self._conflicts[gene["gene"].laboratory][gene["gene"].module][gene["time_slot"]].append(gene["gene"].group)
            self._conflicts[gene["laboratory"]][gene["module"]][gene["time_slot"]].append(gene["group"])
        
        total_penalty = 0
        for laboratory in self._conflicts:
            for module in self._conflicts[laboratory]:
                for time_slot in self._conflicts[laboratory][module]:
                    groups = self._conflicts[laboratory][module][time_slot] #Get all groups that are assigned to the time slot, more specifically, the number of groups in conflict[laboratory][module][time_slot]
                    if len(groups) > self.max_threshold:
                        total_penalty += (len(groups) - self.max_threshold) * self.conflict_penalty
        return total_penalty
    
    def get_conflicts(self):
        return self._conflicts
    
    def configure(self, max_threshold, conflict_penalty):
        """Configure the fitness function
        Args:
            max_threshold (int): Maximum number of groups that can be assigned to a single time slot in lab
            conflict_penalty (int): Penalty for each group that exceeds the maximum threshold"""
        self.max_threshold = max_threshold
        self.conflict_penalty = conflict_penalty
        return self
    
    @classmethod
    def create(cls, config):
        """Create GroupAssignmentConflictFitness instance from configuration
        Args:
            config (dict): Configuration for the fitness function
            config = {
                "max_threshold": 3,
                "conflict_penalty": 1
            }
        """
        fitness = cls()
        return fitness.configure(**config)