from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.api.views import ProjectViewSet, TaskViewSet, CommentViewSet, ProjectMemberViewSet

# Create a router and register the ProjectViewSet
router = DefaultRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<int:project_id>/tasks/', TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='task-detail'),
    path('tasks/<int:task_id>/comments/', CommentViewSet.as_view({'get': 'list', 'post': 'create'}), name='comment-list'),
    path('comments/<int:pk>/', CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'}), name='comment-detail'),
    path('projects/<int:project_id>/members/', ProjectMemberViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('members/<int:pk>/', ProjectMemberViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'update', 'delete': 'destroy'})),
]




