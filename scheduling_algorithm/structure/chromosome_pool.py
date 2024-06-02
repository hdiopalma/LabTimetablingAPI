from scheduling_algorithm.structure.chromosome import Chromosome

class ChromosomePool:
    def __init__(self, chromosome_class: Chromosome, pool_size: int):
        self.pool = [chromosome_class() for _ in range(pool_size)]
        self.pool_size = pool_size
        self.chromosome_class = chromosome_class
        
    def get_chromosome(self) -> Chromosome:
        if self.pool:
            return self.pool.pop()
        else:
            return self.chromosome_class()
        
    def return_chromosome(self, chromosome: Chromosome):
        chromosome.reset()
        self.pool.append(chromosome)