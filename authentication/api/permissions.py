from rest_framework.permissions import BasePermission

class IsAdminOrSelf(BasePermission):
    """
    Custom permission to only allow admins to access or modify any user data.
    Users can only access or modify their own data.
    """
    def has_object_permission(self, request, view, obj):
        # Admins can perform any action
        if request.user.is_staff:
            return True
        
        # Regular users can only view or update their own data
        return obj == request.user