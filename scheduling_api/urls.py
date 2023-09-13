from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register(r'semester', views.SemesterViewSet)
router.register(r'laboratory', views.LaboratoryViewSet)
router.register(r'module', views.ModuleViewSet)
router.register(r'chapter', views.ChapterViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'participant', views.ParticipantViewSet)
router.register(r'assistant',views.AssistantViewSet)
router.register(r'memberships', views.GroupMembershipViewSet)
            

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('semester/', views.SemesterViewSet.as_view({'get': 'list'})),
    path('lab/', views.LaboratoryViewSet.as_view({'get':'list'})),
    path('module/', views.ModuleViewSet.as_view({'get':'list'})),
    path('chapter/', views.ChapterViewSet.as_view({'get':'list'})),
    path('group/', views.GroupViewSet.as_view({'get':'list'})),
    path('participant/', views.ParticipantViewSet.as_view({'get':'list'})),
    path('assistant/', views.AssistantViewSet.as_view({'get':'list'})),
    path('memberships/', views.GroupMembershipViewSet.as_view({'get':'list'}))
]
