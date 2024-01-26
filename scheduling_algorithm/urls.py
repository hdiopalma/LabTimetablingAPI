from django.urls import path
from .views import GenerateTimetabling

urlpatterns = [
    path('generate_timetabling/', GenerateTimetabling.as_view(), name='generate_timetabling'),
]


