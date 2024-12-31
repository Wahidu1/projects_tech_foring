from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.schemas import AutoSchema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()

from authentication.api.serializers import MyUserCreateSerializer, MyUserLoginSerializers, MyUserSerializer
from authentication.models import MyUser

class LoginAPIView(APIView):
    schema = AutoSchema()  # Attach DRF's built-in schema generator
    permission_classes = [AllowAny]
    def get_serializer(self, *args, **kwargs):
        return MyUserLoginSerializers(*args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MyUserCreateView(APIView):
    schema = AutoSchema()  # Attach DRF's built-in schema generator

    def get_serializer(self, *args, **kwargs):
        return MyUserCreateSerializer(*args, **kwargs)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User created successfully",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Limit queryset to the user themselves if desired.
        """
        user = self.request.user
        id = self.kwargs.get('pk')
        
        if not id:
            return MyUser.objects.none()

        user_to_get = MyUser.objects.filter(id=id)
        if not user_to_get.exists():
            return MyUser.objects.none()
        
        if user.is_superuser or user == user_to_get.first():
            return user_to_get
        return MyUser.objects.none()

    def perform_update(self, serializer):
        """
        Ensure that users can only update their own details unless they are admins.
        """
        id = self.kwargs.get('pk')
        user = self.request.user

        if user.is_superuser or user.id == id:
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to edit this user.")

    def delete(self, request, *args, **kwargs):
        """
        Override to customize delete behavior if needed.
        """
        user = self.request.user
        id = self.kwargs.get('pk')
        member = MyUser.objects.filter(id=id)

        if not member.exists():
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_superuser:
            member.first().delete()
            return Response({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "You do not have permission to delete."}, status=status.HTTP_403_FORBIDDEN)

        
