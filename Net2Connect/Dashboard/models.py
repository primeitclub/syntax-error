from Accounts.models import Student
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from Accounts.models import Skill, Student

User = get_user_model()


class Categories(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    ACCESS_TYPE = [
        ('open', 'Open to All'),
        ('invite', 'By Invitation Only'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='owned_projects', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    categories = models.ManyToManyField(
        Categories, blank=True, related_name='projects')
    access_type = models.CharField(
        max_length=10, choices=ACCESS_TYPE, default='invite')
    max_members = models.PositiveIntegerField(default=1)
    points = models.PositiveIntegerField(default=0)

    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='ongoing')

    members = models.ManyToManyField(
        User, related_name='joined_projects', blank=True)
    invited_users = models.ManyToManyField(
        User, related_name='invited_projects', blank=True)

    required_skills = models.ManyToManyField(Skill, blank=True)
    required_fields = models.CharField(max_length=255, blank=True, null=True,
                                       help_text="Comma-separated fields like Web Development, AI, ML")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def invite_user(self, user_or_email):
        if isinstance(user_or_email, User):
            user = user_or_email
        else:
            try:
                user = User.objects.get(email=user_or_email)
            except User.DoesNotExist:
                PendingInvitation.objects.get_or_create(
                    email=user_or_email, project=self)
                return False

        if self.access_type == 'invite' and user not in self.members.all() and user not in self.invited_users.all():
            self.invited_users.add(user)

            student = Student.objects.filter(user=user).first()
            if student:
                Notification.objects.create(
                    student=student,
                    message=f"You have been invited to join the project '{self.title}' by {self.owner.username}."
                )

            if user.email:
                send_mail(
                    subject=f"Invitation to join project '{self.title}'",
                    message=f"Hi {user.username},\n\nYou have been invited by {self.owner.username} to collaborate on the project '{self.title}'.\nPlease log in to accept.\n\nThanks!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            return True
        return False

    def accept_invitation(self, user):
        if user in self.invited_users.all() and self.members.count() < self.max_members:
            self.invited_users.remove(user)
            self.members.add(user)
            return True
        return False

    def reject_invitation(self, user):
        if user in self.invited_users.all():
            self.invited_users.remove(user)
            return True
        return False

    def join_project(self, user):
        if self.members.count() >= self.max_members:
            return False

        if self.access_type == 'invite' and user in self.invited_users.all():
            self.invited_users.remove(user)
            self.members.add(user)
            return True

        if self.access_type == 'open' and user not in self.members.all():
            self.members.add(user)
            return True

        return False

    @property
    def member_count(self):
        return self.members.count()

    @property
    def first_three_members(self):
        return self.members.all()[:3]

    @property
    def progress_percentage(self):
        total = self.tasks.count()
        completed = self.tasks.filter(is_completed=True).count()
        return int((completed / total) * 100) if total > 0 else 0

    def get_member_initials(self, member):
        return getattr(member, 'initials', member.username[:2].upper())

    def mark_completed(self):
        if self.status != 'completed':
            self.status = 'completed'
            self.save()

            
            # Distribute reward points
            members = self.members.all()
            if self.points and members:
                per_member = self.points // members.count()
                for m in members:
                    RewardLog.objects.create(
                        user=m, project=self, points_awarded=per_member)

    class Meta:
        ordering = ['-created_at']


class Task(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PendingInvitation(models.Model):
    email = models.EmailField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.project.title}"


class RewardLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    points_awarded = models.PositiveIntegerField()
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.points_awarded} pts"




class Notification(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.TextField()
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True)  # Add if missing
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.student.user.username}: {self.message[:20]}'


