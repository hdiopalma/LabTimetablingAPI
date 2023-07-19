from algorithm_base import Algorithm

class TabuSearch(Algorithm):
    def __init__(self) -> None:
        super().__init__()
        
    def initialize(self):
        return super().initialize()
        
    def evaluate_fitness(self, solution):
        return super().evaluate_fitness(solution)
    
    def generate_neighborhood(self, solution):
        pass
    
    def evaluate_move(self, move):
        pass
    
    def update_tabu_list(self, move):
        pass
    
    def update_best_solution(self, solution):
        pass
    
    def run(self, iteration):
        return super().run(iteration)
    
    def get_best_solution(self):
        return super().get_best_solution()
    
    def __str__(self) -> str:
        return super().__str__()