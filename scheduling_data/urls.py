from django.urls import path, include
from rest_framework import routers

from . import views
from scheduling_algorithm.views import GenerateTimetabling

router = routers.DefaultRouter()

router.register(r'semester', views.SemesterViewSet)
router.register(r'laboratory', views.LaboratoryViewSet)
router.register(r'module', views.ModuleViewSet)
router.register(r'chapter', views.ChapterViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'participant', views.ParticipantViewSet)
router.register(r'assistant',views.AssistantViewSet)
router.register(r'memberships', views.GroupMembershipViewSet)
router.register(r'solution/schedule_data', views.ScheduleDataViewSet)
router.register(r'solution', views.SolutionViewSet)
            

urlpatterns = [
    #save data
    path('module/save/', views.ModuleViewSet.as_view({'post':'create'})),
    path('chapter/save/', views.ChapterViewSet.as_view({'post':'create'})),
    path('group/save/', views.GroupViewSet.as_view({'post':'create'})),
    path('participant/save/', views.ParticipantViewSet.as_view({'post':'create'})),

    #update data
    path('module/update/<int:pk>/', views.ModuleViewSet.as_view({'put':'update'})),
    path('chapter/update/<int:pk>/', views.ChapterViewSet.as_view({'put':'update'})),
    path('group/update/<int:pk>/', views.GroupViewSet.as_view({'put':'update'})),
    path('participant/<int:pk>/update/', views.ParticipantViewSet.as_view({'put':'update'})),
    path('assistant/update/<int:pk>/', views.AssistantViewSet.as_view({'put':'update'})),
    path('memberships/update/<int:pk>/', views.GroupMembershipViewSet.as_view({'put':'update'})),

    #semester
    path('semester/active/', views.SemesterViewSet.as_view({'get':'active'}), name='active_semester'),
    path('semester/', views.SemesterViewSet.as_view({'get': 'list', 'post': 'create'})),

    #laboratory
    path('laboratory/', views.LaboratoryViewSet.as_view({'get':'list', 'post':'create'})),
    path('laboratory/save/', views.LaboratoryViewSet.as_view({'post':'create'})),
    path('laboratory/update/<int:pk>/', views.LaboratoryViewSet.as_view({'put':'update'})),

    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('module/', views.ModuleViewSet.as_view({'get':'list'})),
    path('chapter/', views.ChapterViewSet.as_view({'get':'list'})),
    path('group/', views.GroupViewSet.as_view({'get':'list'})),
    path('participant/', views.ParticipantViewSet.as_view({'get':'list'})),
    path('assistant/', views.AssistantViewSet.as_view({'get':'list'})),
    path('memberships/', views.GroupMembershipViewSet.as_view({'get':'list'})),
    
    #timetable related data
    
    path('solution/', views.SolutionViewSet.as_view({'get':'list'})),
    path('solution/schedule_data/', views.ScheduleDataViewSet.as_view({'get':'list'})),
]
