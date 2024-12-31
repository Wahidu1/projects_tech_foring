from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.models import Project, ProjectMember, Task, Comment
from app.api.serializers import ProjectSerializer, ProjectMemberSerializer, TaskSerializer, CommentSerializer
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

        
    def destroy(self, request, *args, **kwargs):
        # Retrieve the project instance being deleted
        project = self.get_object()

        # Check if the current user is the owner or a superuser
        if project.owner != request.user and not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete this project.")

        # Perform the delete operation if the user is authorized
        return super().destroy(request, *args, **kwargs)
    
class ProjectMemberViewSet(viewsets.ModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter the members by the projects the authenticated user is part of.
        """
        user = self.request.user
        return ProjectMember.objects.filter(project__projectmember__user=user)

    def perform_create(self, serializer):
        """
        Ensure only project admins can add members.
        """
        project = serializer.validated_data['project']
        user_role = ProjectMember.objects.filter(project=project, user=self.request.user).first()

        if not user_role or user_role.role != 'Admin':
            raise PermissionDenied("Only project admins can add members.")

        serializer.save()

    def perform_update(self, serializer):
        """
        Allow only project admins to update roles.
        """
        project = serializer.instance.project
        user_role = ProjectMember.objects.filter(project=project, user=self.request.user).first()

        if not user_role or user_role.role != 'Admin':
            raise PermissionDenied("Only project admins can update members.")
        
        serializer.save()

    def perform_destroy(self, instance):
        """
        Allow only project admins to remove members.
        """
        project = instance.project
        user_role = ProjectMember.objects.filter(project=project, user=self.request.user).first()

        if not user_role or user_role.role != 'Admin':
            raise PermissionDenied("Only project admins can remove members.")

        instance.delete()



class TaskViewSet(viewsets.ViewSet):
    serializer_class = TaskSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('project_id', openapi.IN_PATH, description="ID of the project", type=openapi.TYPE_INTEGER)
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def list(self, request, project_id=None):
        """Retrieve a list of all tasks in a project."""
        try:
            project = Project.objects.get(id=project_id)
            tasks = Task.objects.filter(project=project)
            serializer = self.serializer_class(tasks, many=True)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(request_body=TaskSerializer, responses={201: TaskSerializer})
    def create(self, request, project_id=None):
        """Create a new task in a project."""
        try:
            project = Project.objects.get(id=project_id)
            data = request.data.copy()
            data['project'] = project.id
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(responses={200: TaskSerializer})
    def retrieve(self, request, pk=None):
        """Retrieve details of a specific task."""
        try:
            task = Task.objects.get(id=pk)
            serializer = self.serializer_class(task)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(request_body=TaskSerializer, responses={200: TaskSerializer})
    def update(self, request, pk=None):
        """Update task details."""
        try:
            task = Task.objects.get(id=pk)
            serializer = self.serializer_class(task, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(responses={204: 'Task deleted successfully'})
    def destroy(self, request, pk=None):
        """Delete a task."""
        try:
            task = Task.objects.get(id=pk)
            task.delete()
            return Response({"message": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)


class CommentViewSet(viewsets.ViewSet):
    serializer_class = CommentSerializer
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('task_id', openapi.IN_PATH, description="ID of the task", type=openapi.TYPE_INTEGER)
        ],
        responses={200: CommentSerializer(many=True)},
    )
    def list(self, request, task_id=None):
        """Retrieve a list of all comments on a task."""
        try:
            task = Task.objects.get(id=task_id)
            comments = Comment.objects.filter(task=task)
            serializer = self.serializer_class(comments, many=True)
            return Response(serializer.data)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(
        request_body=CommentSerializer,
        responses={201: CommentSerializer},
    )
    def create(self, request, task_id=None):
        """Create a new comment on a task."""
        try:
            task = Task.objects.get(id=task_id)
            data = request.data.copy()
            data['task'] = task.id
            data['user'] = request.user.id  # Assuming authenticated user
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(
        responses={200: CommentSerializer},
    )
    def retrieve(self, request, pk=None):
        """Retrieve details of a specific comment."""
        try:
            comment = Comment.objects.get(id=pk)
            serializer = self.serializer_class(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(
        request_body=CommentSerializer,
        responses={200: CommentSerializer},
    )
    def update(self, request, pk=None):
        """Update comment details."""
        try:
            comment = Comment.objects.get(id=pk)
            serializer = self.serializer_class(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
    @swagger_auto_schema(
        responses={204: 'No Content'},
    )
    def destroy(self, request, pk=None):
        """Delete a comment."""
        try:
            comment = Comment.objects.get(id=pk)
            comment.delete()
            return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        


class ProjectMemberViewSet(viewsets.ViewSet):
    serializer_class = ProjectMemberSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('project_id', openapi.IN_PATH, description="ID of the project", type=openapi.TYPE_INTEGER)
        ],
        responses={200: ProjectMemberSerializer(many=True)},
    )
    def list(self, request, project_id=None):
        """Retrieve a list of all members in a project."""
        try:
            project = Project.objects.get(id=project_id)
            members = ProjectMember.objects.filter(project=project)
            serializer = self.serializer_class(members, many=True)
            return Response(serializer.data)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=ProjectMemberSerializer,
        responses={201: ProjectMemberSerializer},
    )
    def create(self, request, project_id=None):
        """Add a new member to a project."""
        try:
            project = Project.objects.get(id=project_id)
            data = request.data.copy()
            data['project'] = project.id
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={200: ProjectMemberSerializer},
    )
    def retrieve(self, request, pk=None):
        """Retrieve details of a specific project member."""
        try:
            member = ProjectMember.objects.get(id=pk)
            serializer = self.serializer_class(member)
            return Response(serializer.data)
        except ProjectMember.DoesNotExist:
            return Response({"error": "Project member not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        request_body=ProjectMemberSerializer,
        responses={200: ProjectMemberSerializer},
    )
    def update(self, request, pk=None):
        """Update project member details."""
        try:
            member = ProjectMember.objects.get(id=pk)
            serializer = self.serializer_class(member, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProjectMember.DoesNotExist:
            return Response({"error": "Project member not found."}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        responses={204: 'No Content'},
    )
    def destroy(self, request, pk=None):
        """Remove a member from a project."""
        try:
            member = ProjectMember.objects.get(id=pk)
            member.delete()
            return Response({"message": "Member removed successfully."}, status=status.HTTP_204_NO_CONTENT)
        except ProjectMember.DoesNotExist:
            return Response({"error": "Project member not found."}, status=status.HTTP_404_NOT_FOUND)
