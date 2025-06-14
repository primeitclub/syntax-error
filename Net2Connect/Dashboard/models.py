from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Accounts.models import Skill
class Categories(models.Model):
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
        User, on_delete=models.CASCADE, related_name='owned_projects', null=True, blank=True)
    
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

    members = models.ManyToManyField(User, related_name='joined_projects', blank=True)
    invited_users = models.ManyToManyField(User, related_name='invited_projects', blank=True)

    # 🔥 Required for Smart Matching:
    required_skills = models.ManyToManyField(Skill, blank=True)
    required_fields = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Comma-separated fields like Web Development, AI, ML"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def invite_user(self, user):
        if self.access_type == 'invite' and user not in self.members.all():
            self.invited_users.add(user)
            return True
        return False

    def join_project(self, user):
        if self.access_type == 'open' and user not in self.members.all() and self.members.count() < self.max_members:
            self.members.add(user)
            return True
        return False
    
    @property
    def member_count(self):
        """Optimized member count using annotation"""
        if hasattr(self, '_member_count'):
            return self._member_count
        return self.members.count()


    @property
    def first_three_members(self):
        """Get first 3 members with optimized query"""
        return self.members.all().select_related('student')[:3]


    @property
    def progress_percentage(self):
        """Calculate completion percentage if you have tasks"""
        if hasattr(self, 'completed_tasks') and hasattr(self, 'total_tasks'):
            if self.total_tasks > 0:
                return int((self.completed_tasks / self.total_tasks) * 100)
        return 0

    def get_member_initials(self, member):
        """Safe way to get member initials"""
        return getattr(member, 'initials', member.username[:2].upper())

    class Meta:
        ordering = ['-created_at']
