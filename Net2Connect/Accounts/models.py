from django.db import models
from django.contrib.auth.models import User

def create_user():
    user = User.objects.create_user("admin","Pravin.admin@gmail.com","admin123")
    user.first_name='Pravin',
    user.last_name = "Gyawali"

    user.save()