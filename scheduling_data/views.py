from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from scheduling_data.models import Semester, Laboratory, Module, Chapter, Group, Participant, Assistant

# Create your views here.

@csrf_exempt
def schedule_practicum(request):
    if request.method == "POST":
        return JsonResponse({"message": "Hello, world!"})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def participant_list(request):
    if request.method == "GET":
        participants = Participant.objects.all()
        data = [{'name' : participant.name,'nim' : participant.nim, 'semester' : participant.semester.name, 'regular_schedule': participant.regular_schedule} for participant in participants]
        
        return JsonResponse(data, safe=False)