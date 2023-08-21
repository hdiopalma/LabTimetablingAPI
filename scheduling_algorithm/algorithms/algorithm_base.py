class Algorithm:
    def __init__(self) -> None:
        pass
    
    def initialize_solution(self):
        raise NotImplementedError("initialize_solution method is not implemented")
    
    def evaluate_fitness(self, solution):
        raise NotImplementedError("evaluate_fitness method is not implemented")
    
    def run(self, iteration):
        raise NotImplementedError("run method is not implemented")
    
    def get_best_solution(self):
        raise NotImplementedError("get_best_solution method is not implemented")
    
    def __str__(self) -> str:
        pass
    