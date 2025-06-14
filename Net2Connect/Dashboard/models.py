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
    User, 
    on_delete=models.CASCADE, 
    related_name='owned_projects',
    null=True,  # Add this temporarily
    blank=True  # Add this temporarily
    )
    members = models.ManyToManyField(
        User,
        related_name='projects',
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    access_type = models.CharField(
        max_length=10, 
        choices=ACCESS_TYPE, 
        default='invite'
    )
    max_members = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='ongoing'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def progress(self):
        try:
            total_tasks = self.tasks.count()
            if total_tasks == 0:
                return 0
            completed_tasks = self.tasks.filter(status='completed').count()
            return int((completed_tasks / total_tasks) * 100)
        except:
            return 0