from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def schedule_practicum(request):
    if request.method == "POST":
        return JsonResponse({"message": "Hello, world!"})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
