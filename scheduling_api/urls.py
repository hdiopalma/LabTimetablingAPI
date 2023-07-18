from django.urls import path, include
from rest_framework import routers

from .views import *

router = routers.DefaultRouter()

router.register(r'semester', SemesterViewSet)
router.register(r'laboratory', LaboratoryViewSet)
router.register(r'module', ModuleViewSet)
router.register(r'chapter', ChapterViewSet)
router.register(r'group', GroupViewSet)
router.register(r'participant', ParticipantViewSet)
router.register(r'assistant',AssistantViewSet)
router.register(r'memberships', GroupMembershipViewSet)
            

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('semester/', SemesterViewSet.as_view({'get': 'list'})),
    path('lab/', LaboratoryViewSet.as_view({'get':'list'})),
    path('module/', ModuleViewSet.as_view({'get':'list'})),
    path('chapter/', ChapterViewSet.as_view({'get':'list'})),
    path('group/', GroupViewSet.as_view({'get':'list'})),
    path('participant/', ParticipantViewSet.as_view({'get':'list'})),
    path('assistant/', AssistantViewSet.as_view({'get':'list'})),
    path('memberships/', GroupMembershipViewSet.as_view({'get':'list'}))
]
