from django.db import models

from authentication.models import MyUser


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectMember(models.Model):
    role_choice = [
        ('Admin', 'Admin'),
        ('Member', 'Member'),
        ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=role_choice)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Task(models.Model):
    status_choice = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ]
    priority_choice = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=status_choice)
    priority = models.CharField(max_length=50, choices=priority_choice)
    assigned_to = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)