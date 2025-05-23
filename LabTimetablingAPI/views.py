# HttpResponse is used to render the response HTTP Request
from django.http import HttpResponse

#Function is being initialised to perform a return request when called


def PythonGeeks(request) :
  return HttpResponse("Welcome to my world")