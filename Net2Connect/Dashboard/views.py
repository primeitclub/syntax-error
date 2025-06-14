from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Category
from django.http import JsonResponse
from django.db import models

# Create your views here.

@login_required
def add_project(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        privacy = request.POST.get('privacy')
        
        try:
            category = Category.objects.get(id=category_id)
            project = Project.objects.create(
                title=title,
                category=category,
                description=description,
                privacy=privacy,
                created_by=request.user
            )
            project.members.add(request.user)  # Add creator as a member
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            return redirect('add_project')
    
    categories = Category.objects.all()
    return render(request, 'Dashboard/add_project.html', {
        'categories': categories,
        'privacy_choices': Project.PRIVACY_CHOICES
    })

@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user is the creator or a member
    if request.user != project.created_by and request.user not in project.members.all():
        messages.error(request, 'You do not have permission to update this project.')
        return redirect('project_list')
    
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
    return render(request, 'Dashboard/update_project.html', {
        'project': project,
        'categories': categories,
        'privacy_choices': Project.PRIVACY_CHOICES
    })

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'Dashboard/project_detail.html', {
        'project': project
    })

@login_required
def project_list(request):
    # Get projects where user is creator or member
    user_projects = Project.objects.filter(
        models.Q(created_by=request.user) | 
        models.Q(members=request.user)
    ).distinct()
    
    return render(request, 'Dashboard/project_list.html', {
        'projects': user_projects
    })
