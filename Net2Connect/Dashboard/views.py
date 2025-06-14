from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Category
from django.http import JsonResponse
from django.db import models

def dashboard(request):
    return render(request,'dashboard.html')

def feed(request):
    return render(request,'feed.html')

def collab(request):
    return render(request,'collab.html')

def group(request):
    return render(request,'group.html')

def inbox(request):
    return render(request,'inbox.html')

def notification(request):
    return render(request,'notification.html')

def settings(request):
    return render(request,'settings.html')

def logout_view(request):
    return render(request,'logout.html')

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
            category = Category.objects.get(id=category_id)
            project.title = title
            project.category = category
            project.description = description
            project.privacy = privacy
            project.save()
            
            messages.success(request, 'Project updated successfully!')
            return redirect('project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')
    
    categories = Category.objects.all()
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

    
def home_view(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You are not allowed to access this page.")
    return render(request, 'home.html')
