from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

router.register(r'semester', SemesterViewSet)
router.register(r'participant', ParticipantViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('semester/', SemesterViewSet.as_view({'get': 'list'})),
    path('participant/', ParticipantViewSet.as_view({'get':'list'}))
]
