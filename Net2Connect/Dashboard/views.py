from django.db.models import Q
from Dashboard.models import Project
from .models import Project
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Categories
from django.http import JsonResponse
from django.db import models
from Accounts.models import Student


def dashboard(request):
    return render(request, 'dashboard.html')


@login_required
def feed(request):
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return render(request, 'feed.html', {
            'suggested_projects': [],
            'suggested_creators': [],
            'message': "Student profile not found."
        })

    search_query = request.GET.get('q', '').strip().lower()

    if search_query:
        # Search in projects (title, description, required fields, required skills)
        projects = Project.objects.filter(status='completed').filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(required_fields__icontains=search_query) |
            Q(required_skills__name__icontains=search_query)
        ).distinct()

        # Search in students (username, interest fields, skills)
        creators = Student.objects.exclude(id=student.id).filter(
            Q(user__username__icontains=search_query) |
            Q(user_name__icontains=search_query) |
            Q(interest_fields__icontains=search_query) |
            Q(skills__name__icontains=search_query)
        ).distinct()

        suggested_projects = projects[:6]
        suggested_creators = creators[:6]

    else:
        # Your existing scoring-based recommendations

        student_skills = set(student.skills.all())
        student_fields = set(f.strip().lower()
                             for f in (student.interest_fields or "").split(","))

        # Suggest completed projects
        completed_projects = Project.objects.filter(status='completed')
        project_suggestions = []

        for project in completed_projects:
            project_skills = set(project.required_skills.all())
            project_fields = set(f.strip().lower() for f in (
                project.required_fields or "").split(","))

            score = (
                len(student_skills & project_skills) * 2 +
                len(student_fields & project_fields)
            )

            if score > 0:
                project_suggestions.append((project, score))

        project_suggestions.sort(key=lambda x: x[1], reverse=True)
        suggested_projects = [proj for proj, _ in project_suggestions[:6]]

        # Suggest creators (other students)
        all_students = Student.objects.exclude(id=student.id)
        creator_suggestions = []

        for s in all_students:
            match_skills = len(student_skills & set(s.skills.all()))
            s_fields = set(f.strip().lower()
                           for f in (s.interest_fields or "").split(","))
            match_fields = len(student_fields & s_fields)
            score = match_skills * 2 + match_fields

            if score > 0:
                creator_suggestions.append((s, score))

        creator_suggestions.sort(key=lambda x: x[1], reverse=True)
        suggested_creators = [s for s, _ in creator_suggestions[:6]]

    return render(request, 'feed.html', {
        'student': student,
        'suggested_projects': suggested_projects,
        'suggested_creators': suggested_creators,
        'search_query': search_query,
    })


def collab(request):
    return render(request, 'collab.html')


def group(request):
    return render(request, 'group.html')


def inbox(request):
    return render(request, 'inbox.html')


def notification(request):
    return render(request, 'notification.html')


def settings(request):
    return render(request, 'settings.html')


def logout_view(request):
    return render(request, 'logout.html')

# Removed @login_required for testing


@login_required
def add_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        privacy = request.POST.get('privacy')

        try:
            # For testing, use the first user in the database
            test_user = User.objects.first()
            if not test_user:
                messages.error(request, 'No test user found in database')
                return redirect('add_project')

            category = Category.objects.get(id=category_id)
            project = Project.objects.create(
                title=title,
                category=category,
                description=description,
                privacy=privacy,
                created_by=test_user
            )
            project.members.add(test_user)
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            return redirect('add_project')

    categories = Category.objects.all()
    return render(request, 'add_project.html', {
        'categories': categories,
        'privacy_choices': Project.PRIVACY_CHOICES
    })

# Removed @login_required for testing


@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        privacy = request.POST.get('privacy')

        try:
            category = Categories.objects.get(id=category_id)
            project.title = title
            project.category = category
            project.description = description
            project.privacy = privacy
            project.save()

            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')

    categories = Categories.objects.all()
    return render(request, 'update_project.html', {
        'project': project,
        'categories': categories,
        'privacy_choices': Project.PRIVACY_CHOICES
    })

# Removed @login_required for testing


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'project_detail.html', {
        'project': project
    })

# Removed @login_required for testing


def project_list(request):
    projects = Project.objects.all()
    return render(request, 'project_list.html', {
        'projects': projects
    })@login_required(login_url='/')


@login_required(login_url='/')
def home_view(request):
    student_data = Student.objects.filter(user=request.user).first()

    if not student_data:
        return HttpResponse("Student profile not found. Please contact admin.", status=404)

    context = {
        'student': student_data
    }
    return render(request, 'dashboard.html', context)
