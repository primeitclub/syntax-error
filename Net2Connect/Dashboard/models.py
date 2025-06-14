from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Project(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    ACCESS_TYPE = [
        ('open', 'Open to All'),
        ('invite', 'By Invitation Only'),
    ]

    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    access_type = models.CharField(
        max_length=10, choices=ACCESS_TYPE, default='invite')
    max_members = models.PositiveIntegerField(default=1)

    points = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='ongoing')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def invite_user(self, user):
        if self.privacy == 'private' and user not in self.members.all():
            self.invited_users.add(user)
            return True
        return False

    def join_project(self, user):
        if self.privacy == 'public':
            self.members.add(user)
            return True
        return False

