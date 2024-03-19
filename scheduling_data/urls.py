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
    path('module/', views.ModuleViewSet.as_view({'get':'list'})),
    path('chapter/', views.ChapterViewSet.as_view({'get':'list'})),
    path('group/', views.GroupViewSet.as_view({'get':'list'})),
    path('participant/', views.ParticipantViewSet.as_view({'get':'list'})),
    path('assistant/', views.AssistantViewSet.as_view({'get':'list'})),
    path('memberships/', views.GroupMembershipViewSet.as_view({'get':'list'})),

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
    path('semester/', views.SemesterViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('semester/save/', views.SemesterViewSet.as_view({'post':'create'})),
    path('semester/update/<int:pk>/', views.SemesterViewSet.as_view({'put':'update'})),
    path('semester/count/', views.SemesterViewSet.as_view({'get':'count'})),
    path('semester/<int:pk>/count/module/', views.SemesterViewSet.as_view({'get':'count_module'})),
    path('semester/<int:pk>/count/group/', views.SemesterViewSet.as_view({'get':'count_group'})),
    path('semester/<int:pk>/count/participant/', views.SemesterViewSet.as_view({'get':'count_participant'})),
    path('semester/<int:pk>/count/all', views.SemesterViewSet.as_view({'get':'count_all'})),
    path('semester/<int:pk>/count/', views.SemesterViewSet.as_view({'get':'count_all'})),

    #laboratory
    path('laboratory/', views.LaboratoryViewSet.as_view({'get':'list', 'post':'create'})),
    path('laboratory/save/', views.LaboratoryViewSet.as_view({'post':'create'})),
    path('laboratory/update/<int:pk>/', views.LaboratoryViewSet.as_view({'put':'update'})),
    path('laboratory/count/', views.LaboratoryViewSet.as_view({'get':'count'})),
    path('laboratory/<int:pk>/count/module/', views.LaboratoryViewSet.as_view({'get':'count_module'})),
    path('laboratory/<int:pk>/count/assistant/', views.LaboratoryViewSet.as_view({'get':'count_assistant'})),
    path('laboratory/<int:pk>/count/group/', views.LaboratoryViewSet.as_view({'get':'count_group'})),
    path('laboratory/<int:pk>/count/participant/', views.LaboratoryViewSet.as_view({'get':'count_participant'})),
    path('laboratory/<int:pk>/count/all', views.LaboratoryViewSet.as_view({'get':'count_all'})),
    path('laboratory/<int:pk>/count/', views.LaboratoryViewSet.as_view({'get':'count_all'})),
]
