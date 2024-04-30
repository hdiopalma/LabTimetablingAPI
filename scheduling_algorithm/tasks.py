from huey import RedisHuey
from huey.contrib.djhuey import task

from scheduling_algorithm.utils.solution_generator import SolutionGenerator
from .config_schema import ScheduleConfiguration

import time

huey = RedisHuey()


@task()
def generate_timetabling_from_data(data: dict):
    """Generates a timetabling solution and saves it to the database.

    Args:
        data (dict): The configuration data for the timetabling problem.

    Returns:
        Solution: The generated solution data.
    """
    data = ScheduleConfiguration.from_data(data)
    generator = SolutionGenerator(data)
    solution_data = generator.create_solution()
    
    message = {
        "status": "success", # "error"
        "message": "Task submitted successfully",
        "solution_id": solution_data.id,
        "solution_name": solution_data.name
    }

    solution_result = generator.generate_solution()

    return solution_data

@task()
def generate_timetabling_from_object(generator: SolutionGenerator):
    """Generates a timetabling solution and saves it to the database.

    Args:
        generator (SolutionGenerator): The solution generator object.

    Returns:
        Solution: The generated solution data.
    """
    solution = generator.generate_solution()

    return solution