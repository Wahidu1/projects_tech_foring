from rest_framework import serializers
from authentication.models import MyUser
from authentication.api.serializers import MyUserSerializer
from app.models import Project, ProjectMember, Task, Comment

class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)  # Use a related field or keep read_only

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['owner']
        
    def update(self, instance, validated_data):
        # Allow only superusers to change the owner field
        owner_data = validated_data.get('owner')
        if owner_data:
            if not self.context['request'].user.is_superuser:
                raise serializers.ValidationError("Only superusers can change the owner.")
            # Ensure that the owner exists in the database
            validated_data['owner'] = MyUser.objects.get(id=owner_data['id'])
        
        # Update other fields
        return super().update(instance, validated_data)


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assigned_to', 'project', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'task', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        
class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'user', 'role', 'created_at', 'updated_at']
