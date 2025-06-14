from datetime import timedelta
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# User Creation


def create_user():
    user = User.objects.create_user(
        "admin", "Pravin.admin@gmail.com", "admin123")
    user.first_name = 'Pravin'
    user.last_name = "Gyawali"

    user.save()

# Skill Model


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    points = models.IntegerField(default=10)
    
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    interest_fields = models.CharField(max_length=255, blank=True, null=True)
    number_of_connections = models.IntegerField(default=0)
    website_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    date_joined = models.DateTimeField(default=timezone.now)
    last_active = models.DateTimeField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def username(self):
        return self.user.username
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def is_profile_complete(self):
        def is_nonempty(field):
            return bool(field and field.strip())

        required_fields = [
            self.description,
            self.interest_fields,
            self.address,
            self.website_url,
            self.github_url,
            self.linkedin_url,
        ]

        return all(is_nonempty(field) for field in required_fields) and self.skills.exists()

    
# EMail OTP
class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)  # 6 digit OTP
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.user.email}"
