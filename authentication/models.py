from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from authentication.managers import MyUserManager

class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Controls access to admin
    is_superuser = models.BooleanField(default=False)  # Grants full permissions
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'  # The field used to log in
    REQUIRED_FIELDS = ['email']  # Additional fields required when creating a user

    objects = MyUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        """
        Returns True if the user has a specific permission.
        Admins have all permissions.
        """
        if self.is_superuser:
            return True
        return self.is_staff  # Admins or staff can perform any action

    def has_module_perms(self, app_label):
        """
        Returns True if the user has permissions to view the app label.
        Admins have full access.
        """
        if self.is_superuser:
            return True
        return self.is_staff  # Admins or staff can access any module
