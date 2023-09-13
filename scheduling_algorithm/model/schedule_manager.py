# Generate Schedule chromosome
class Schedule:
    # Initializes chromosomes with configuration block (setup of chromosome)
    def __init__(self, config):
        self.config = config
        self.chromosome = []
        self.fitness = 0.0