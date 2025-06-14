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
from Accounts.models import Student

from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime



def dashboard(request):
    return render(request,'dashboard.html')

def feed(request):
    return render(request,'feed.html')

def collab(request):
    print("Hello")
    ongoing_projects = Project.objects.filter(status='ongoing') 
    completed_projects = Project.objects.filter(status='completed')

    print("Ongoing Projects:", ongoing_projects)  # 🔍 This will print in terminal
    print("Completed Projects:", completed_projects)
    print("Ongoing:", ongoing_projects.count(), "Completed:", completed_projects.count())
    return render(request, 'collab.html', {
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects
    })
 

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
        try:
            # Get form data
            title = request.POST['title']
            description = request.POST.get('description', '')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            access_type = request.POST['access_type']
            max_members = request.POST.get('max_members', 1)
            category_ids = request.POST.getlist('categories')  # Get list of category IDs
            
            # Create project (without categories first)
            project = Project.objects.create(
                owner=request.user,
                title=title,
                description=description,
                start_date=start_date or None,
                end_date=end_date or None,
                access_type=access_type,
                max_members=max_members
            )
            
            # Add categories (many-to-many relationship)
            for category_id in category_ids:
                category = Category.objects.get(id=category_id)
                project.categories.add(category)
            
            project.members.add(request.user)
            messages.success(request, 'Project created successfully!')
            return redirect('dashboard:collabs')
            
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            return redirect('dashboard:add_project')
    
    categories = Category.objects.all()
    return render(request, 'add_project.html', {'categories': categories})

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







@login_required
def collabs_view(request):
    print("Hello")
    ongoing_projects = Project.objects.filter(status='ongoing') 
    completed_projects = Project.objects.filter(status='completed')

    print("Ongoing Projects:", ongoing_projects)  # 🔍 This will print in terminal
    print("Completed Projects:", completed_projects)
    print("Ongoing:", ongoing_projects.count(), "Completed:", completed_projects.count())
    return render(request, 'dashboard/collabs.html', {
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects
    })



@login_required
def project_detail(request, project_id):
    """View to display project details"""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
        context = {
            'project': project,
        }
        return render(request, 'project_detail.html', context)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found')
        return redirect('collabs')

@login_required
def update_project_status(request, project_id):
    """Update project status (ongoing/completed)"""
    if request.method == 'POST':
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
            new_status = request.POST.get('status')
            
            if new_status in ['ongoing', 'completed']:
                project.status = new_status
                project.save()
                return JsonResponse({'success': True, 'message': f'Project marked as {new_status}'})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'})
                
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Project not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def create_project(request):
    if request.method == 'POST':
        try:
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'login_required': True
                }, status=401)
            
            # Parse JSON data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON data'
                }, status=400)
            
            # Validate required fields
            if not data.get('title'):
                return JsonResponse({
                    'success': False,
                    'error': 'Project title is required'
                }, status=400)
            
            # Create project
            project = Project.objects.create(
                owner=request.user,
                title=data['title'],
                description=data.get('description', ''),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                access_type='invite' if data.get('access_type') == 'private' else 'open',
                status='ongoing'
            )
            
            # Add members if private project
            if data.get('access_type') == 'private' and data.get('fellows'):
                for email in data['fellows']:
                    try:
                        user = User.objects.get(email=email.strip().lower())
                        project.members.add(user)
                    except User.DoesNotExist:
                        pass
            
            return JsonResponse({
                'success': True,
                'project': {
                    'id': project.id,
                    'title': project.title,
                    'status': project.status,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)