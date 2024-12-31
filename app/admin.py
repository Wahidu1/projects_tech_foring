from django.contrib import admin
from django.contrib import admin
from app.models import Project, ProjectMember, Task, Comment

admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Task)
admin.site.register(Comment)