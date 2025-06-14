from django.db.models import Q
from .models import Project


def get_suggested_projects(student, limit=6):
    student_skills = set(student.skills.all())
    student_fields = set([f.strip().lower() for f in (student.interest_fields or "").split(",")])

    suggested = []

    for project in Project.objects.filter(status='completed'):
        project_skills = set(project.required_skills.all())
        project_fields = set([f.strip().lower() for f in (project.required_fields or "").split(",")])

        score = len(student_skills & project_skills) * 2 + len(student_fields & project_fields)
        if score > 0:
            suggested.append((project, score))

    suggested.sort(key=lambda x: x[1], reverse=True)
    return [proj for proj, _ in suggested[:limit]]
