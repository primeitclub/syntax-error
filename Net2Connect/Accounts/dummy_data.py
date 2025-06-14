from django.contrib.auth.models import User
from .models import Student, Skill
from django.utils import timezone

def create_dummy_data():
    # Create some skills if not exist
    skills_list = ["Python", "Django", "React", "CSS", "Project Management"]
    skills_objs = []
    for skill_name in skills_list:
        skill, created = Skill.objects.get_or_create(name=skill_name)
        skills_objs.append(skill)

    # Create dummy users + Student profiles
    users_data = [
        {"username": "pravin1", "email": "pravin1@example.com", "first_name": "Pravin", "last_name": "Gyawali", "skills": ["Python", "Django"]},
        {"username": "laxmi", "email": "laxmi@example.com", "first_name": "Laxmi", "last_name": "Shrestha", "skills": ["React", "CSS"]},
        {"username": "suman", "email": "suman@example.com", "first_name": "Suman", "last_name": "Thapa", "skills": ["Project Management"]},
        {"username": "ritu", "email": "ritu@example.com", "first_name": "Ritu", "last_name": "Karki", "skills": ["Python", "React", "CSS"]},
    ]

    for udata in users_data:
        user, created = User.objects.get_or_create(
            username=udata["username"],
            defaults={
                "email": udata["email"],
                "first_name": udata["first_name"],
                "last_name": udata["last_name"],
            }
        )
        if created:
            user.set_password("test1234")
            user.save()

        # Create or get Student profile
        student, _ = Student.objects.get_or_create(
            user=user,
            defaults={
                "user_name": udata["username"],
                "email": udata["email"],
                "points": 10,
                "date_joined": timezone.now(),
            }
        )

        # Assign skills
        student.skills.clear()
        for skill_name in udata["skills"]:
            skill = Skill.objects.get(name=skill_name)
            student.skills.add(skill)

        student.save()

    print("Dummy users and students created successfully!")

