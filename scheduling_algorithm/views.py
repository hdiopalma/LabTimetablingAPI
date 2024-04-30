from rest_framework.permissions import AllowAny

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

import cProfile

from .tasks import generate_timetabling_from_data, generate_timetabling_from_object
from .config_schema import ScheduleConfiguration
from .utils.solution_generator import SolutionGenerator

from huey.contrib.djhuey import HUEY

class GenerateTimetabling(APIView):
    permission_classes = [AllowAny]
    
    # use huey to generate solution
    def post(self, request):
        try:
            generator = SolutionGenerator.from_data(request.data)
            solution = generator.create_solution()
            generate_timetabling_from_object(generator)
            print("Solution: ", solution)
            
            message = {
                "status": "success",
                "message": "Task submitted successfully",
                "solution_id": solution.id,
                "solution_name": solution.name
            }
            
            return Response(message, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # def post(self, request):
    #     data = ScheduleConfiguration.from_data(request.data) # Parse and validate the data
    #     generator = SolutionGenerator(data)
    #     try:
    #         # profiler = cProfile.Profile()
    #         # profiler.enable()
    #         solution = generator.generate_solution()
    #         # profiler.disable()
    #         # profiler.dump_stats("profile.prof")
                
    #         return Response({
    #             "best_fitness": solution.best_fitness,
    #             "time_elapsed": solution.time_elapsed,
    #             "best_solution": generator.best_chromosome.to_json()
    #         }, status=status.HTTP_200_OK)
        
    #     except Exception as e:
    #         print("Error: ", str(e))
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
