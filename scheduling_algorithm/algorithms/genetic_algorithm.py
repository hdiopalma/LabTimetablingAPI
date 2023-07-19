from algorithm_base import Algorithm

class GeneticAlgorithm(Algorithm):
    
    def __init__(self) -> None:
        super().__init__()
        
    def initialize(self):
        pass
    
    def evaluate_fitness(self, solution):
        return super().evaluate_fitness(solution)
    
    def select_parents(self, population):
        pass
    
    def crossover(self, parents):
        pass
    
    def mutate(self, solution):
        pass
    
    def run(self, iteration):
        return super().run(iteration)
    
    def get_best_solution(self):
        return super().get_best_solution()
    
    def __str__(self) -> str:
        return super().__str__()