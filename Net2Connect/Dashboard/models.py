from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from Accounts.models import Skill
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

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
    categories = models.ManyToManyField(Categories, blank=True, related_name='projects')
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

    def invite_user(self, user_or_email):
        user = None
        UserModel = get_user_model()

        if isinstance(user_or_email, UserModel):
            user = user_or_email
        else:
            # Assume email string
            try:
                user = UserModel.objects.get(email=user_or_email)
            except UserModel.DoesNotExist:
                # Optionally: create a PendingInvitation to handle invites for emails not yet registered
                return False

        if self.access_type == 'invite' and user not in self.members.all() and user not in self.invited_users.all():
            self.invited_users.add(user)

            # Create Notification
            student = Student.objects.filter(user=user).first()
            if student:
                Notification.objects.create(
                    student=student,
                    message=f"You have been invited to join the project '{self.title}' by {self.owner.username}."
                )

            # Send email invitation (you can improve by using async tasks like Celery)
            if user.email:
                send_mail(
                    subject=f"Invitation to join project '{self.title}'",
                    message=f"Hi {user.username},\n\nYou have been invited by {self.owner.username} to collaborate on the project '{self.title}'.\nPlease log in to your account to accept the invitation.\n\nThanks!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            return True

        return False

    def accept_invitation(self, user):
        """
        User accepts an invitation.
        Moves user from invited_users to members if there's space.
        """
        if user in self.invited_users.all() and self.members.count() < self.max_members:
            self.invited_users.remove(user)
            self.members.add(user)
            return True
        return False

    def reject_invitation(self, user):
        """
        User rejects an invitation.
        Removes user from invited_users.
        """
        if user in self.invited_users.all():
            self.invited_users.remove(user)
            return True
        return False

    def join_project(self, user):
        if self.members.count() >= self.max_members:
            return False

        # For invited users
        if self.access_type == 'invite' and user in self.invited_users.all():
            self.invited_users.remove(user)
            self.members.add(user)
            return True

        # For public (open) projects
        if self.access_type == 'open' and user not in self.members.all():
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
        return self.members.all()[:3]

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




from django.db import models
from Accounts.models import Student
from Dashboard.models import Project

class Notification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)  # Add if missing
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.student.user.username}: {self.message[:20]}'

