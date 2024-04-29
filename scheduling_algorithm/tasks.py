from huey import RedisHuey
from huey.contrib.djhuey import task

from scheduling_algorithm.utils.solution_generator import SolutionGenerator
from .config_schema import ScheduleConfiguration

import time

huey = RedisHuey()


@task()
def generate_timetabling_task(data: dict):
    """Generates a timetabling solution and saves it to the database.

    Args:
        data (dict): The configuration data for the timetabling problem.

    Returns:
        Solution: The generated solution data.
    """
    data = ScheduleConfiguration.from_data(data)
    generator = SolutionGenerator(data)
    solution = generator.generate_solution()

    return solution