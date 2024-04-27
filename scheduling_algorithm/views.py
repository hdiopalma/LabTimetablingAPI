from rest_framework.permissions import AllowAny

# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

#Json schema for configuration, used for validation and default value

from .config_schema import ScheduleConfiguration

from .utils.solution_generator import SolutionGenerator

class GenerateTimetabling(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = ScheduleConfiguration.from_data(request.data) # Parse and validate the data
        generator = SolutionGenerator(data)
        try:
            solution = generator.generate_solution()
            return Response({
                "best_fitness": solution.best_fitness,
                "time_elapsed": solution.time_elapsed,
                "best_solution": generator.best_chromosome.to_json()
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print("Error: ", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
