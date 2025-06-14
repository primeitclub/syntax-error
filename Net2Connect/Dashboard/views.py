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
        #  Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        access_type = request.POST.get('access_type', 'invite')
        max_members = request.POST.get('max_members', 1)
        fellows_input = request.POST.get('fellows', '').strip()
            
        
    #  Validate required fields
        if not title:
            messages.error(request, 'Project title is required')
            return redirect('dashboard:collab')
            
        # Convert dates
        start_date_obj = None
        end_date_obj = None
        try:
            if start_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format (use YYYY-MM-DD)')
            return redirect('dashboard:collab')
            
        # Validate dates
        if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
            messages.error(request, 'Start date cannot be after end date')
            return redirect('dashboard:collab')
            
        # Create project
        project = Project.objects.create(
            owner=request.user,
            title=title,
            description=description,
            start_date=start_date_obj,
            end_date=end_date_obj,
            access_type=access_type,
            max_members=int(max_members),
            status='ongoing'
        )
            
        # Handle members for private projects
        if access_type == 'invite' and fellows_input:
            fellows_emails = [email.strip() for email in fellows_input.split(',') if email.strip()]
            for email in fellows_emails:
                try:
                    user = User.objects.get(email=email.lower())
                    project.members.add(user)
                except User.DoesNotExist:
                    # You might want to create invitations for non-existing users
                    pass
            
        messages.success(request, 'Project created successfully!')
        # return redirect('dashboard:collab')
    return render(request, 'add_project.html', {

        # 'privacy_choices': Project.PRIVACY_CHOICES
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