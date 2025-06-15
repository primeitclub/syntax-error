import json
from .forms import TaskForm
from .models import Project
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
# adjust import if your Student model is elsewhere
from Accounts.models import Student
from Dashboard.models import Project, Categories, Skill, Notification
from .models import Notification
from connections.models import ConnectionRequest
from .models import Student, Project
from django.db.models import Q, Count, F
from django.shortcuts import get_object_or_404, redirect
from .models import Project, Categories, Skill
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch, Q
from django.db.models import Q, Count, F, Prefetch
from django.db.models import Prefetch
from Accounts.models import Skill  # Assuming Skill model is here
from django.shortcuts import render, redirect
from Accounts.models import Skill
from django.db.models import Count, Prefetch
from django.db.models import Prefetch, Count
from django.db.models import Count
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
from .models import Categories
from Accounts.models import Student
from .models import Task


def dashboard(request):
    student = Student.objects.filter(user=request.user).first()
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

    # Get connected student IDs
    connected_ids = set(student.connections.values_list('id', flat=True))

    # Get pending connection requests sent by current user (User object, not Student)
    pending_sent_requests_user_ids = set(
        ConnectionRequest.objects.filter(from_user=request.user, accepted=None)
        .values_list('to_user_id', flat=True)
    )

    # Map pending user IDs to student IDs
    pending_sent_student_ids = set(
        Student.objects.filter(
            user__id__in=pending_sent_requests_user_ids).values_list('id', flat=True)
    )

    # Projects already joined by student
    joined_project_ids = set(
        request.user.joined_projects.values_list('id', flat=True))

    if search_query:
        # Search-based filtering for projects
        projects = Project.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(required_fields__icontains=search_query) |
            Q(required_skills__name__icontains=search_query)
        ).exclude(
            id__in=joined_project_ids
        ).distinct()

        # Search-based filtering for creators
        creators = Student.objects.exclude(id=student.id).exclude(
            id__in=connected_ids.union(pending_sent_student_ids)
        ).filter(
            Q(user__username__icontains=search_query) |
            Q(user_name__icontains=search_query) |
            Q(interest_fields__icontains=search_query) |
            Q(skills__name__icontains=search_query)
        ).distinct()

        suggested_projects = projects
        suggested_creators = creators[:6]

    else:
        # Show all projects except those already joined
        all_projects = Project.objects.exclude(
            id__in=joined_project_ids).prefetch_related('required_skills')
        suggested_projects = all_projects

        # Suggest creators based on matching skills and fields, not connected or requested
        student_skills = set(student.skills.all())
        student_fields = set(f.strip().lower()
                             for f in (student.interest_fields or "").split(","))

        all_students = Student.objects.exclude(
            id=student.id
        ).exclude(
            id__in=connected_ids.union(pending_sent_student_ids)
        ).prefetch_related('skills')

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


@login_required
def notification(request):
    student = Student.objects.filter(user=request.user).first()
    if not student:
        return render(request, 'notification.html', {'notifications': [], 'error': "Student profile not found."})

    notifications = Notification.objects.filter(student=student).select_related(
        'project', 'project__owner').order_by('-created_at')
    return render(request, 'notification.html', {'notifications': notifications})


@login_required
def dismiss_notifications(request):
    student = Student.objects.filter(user=request.user).first()
    if request.method == 'POST' and student:
        Notification.objects.filter(
            student=student, is_read=False).update(is_read=True)
    return redirect('dashboard:notification')

# Notification Detail view


@login_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, student__user=request.user)
    notification.is_read = True
    notification.save()

    return render(request, 'notification_detail.html', {'notification': notification})


def settings(request):
    return render(request, 'settings.html')


def logout_view(request):
    return render(request, 'logout.html')

# Removed @login_required for testing


@login_required
def collab(request):
    user = request.user
    projects_qs = Project.objects.annotate(
        _member_count=Count('members')
    ).prefetch_related(
        Prefetch('members', queryset=User.objects.select_related('student'))
    )

    # 1. Projects user owns
    owned_projects = projects_qs.filter(owner=user)

    # 2. Projects user is a member but NOT owner
    working_projects = projects_qs.filter(members=user).exclude(owner=user)

    # 3. Invited projects (if you want to show invitations)
    invited_projects = projects_qs.filter(invited_users=user)

    skills = Skill.objects.all()

    return render(request, 'collab.html', {
        'owned_projects': owned_projects,
        'working_projects': working_projects,
        'invited_projects': invited_projects,
        'skills': skills,
    })


@login_required
def add_project(request):
    if request.method == 'POST':
        try:
            title = request.POST['title']
            description = request.POST.get('description', '')
            start_date = request.POST.get('start_date') or None
            end_date = request.POST.get('end_date') or None
            access_type = request.POST['access_type']
            max_members = int(request.POST.get('max_members', 1))
            required_fields = request.POST.get('required_fields', '')

            category_ids = request.POST.getlist('categories')
            skill_ids = request.POST.getlist('required_skills')
            invitees_input = request.POST.get('invitees', '')

            # Create the project
            project = Project.objects.create(
                owner=request.user,
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                access_type=access_type,
                max_members=max_members,
                required_fields=required_fields
            )

            # Set categories
            if category_ids:
                categories = Categories.objects.filter(id__in=category_ids)
                project.categories.set(categories)

            # Set required skills
            if skill_ids:
                skills = Skill.objects.filter(id__in=skill_ids)
                project.required_skills.set(skills)

            # Add project creator as member
            project.members.add(request.user)

            # Handle invitations
            invited_count = 0
            UserModel = get_user_model()
            invitees = [x.strip()
                        for x in invitees_input.split(',') if x.strip()]

            for identifier in invitees:
                # Lookup user by username or email
                user = UserModel.objects.filter(username=identifier).first() or \
                    UserModel.objects.filter(email=identifier).first()

                if user and user != request.user:
                    # Use your invite_user method to add invited user (implement it in Project model)
                    if project.invite_user(user):
                        invited_count += 1

                        # Send invitation email
                        if user.email:
                            send_mail(
                                subject=f"You're invited to collaborate on '{project.title}'",
                                message=(
                                    f"Hi {user.username},\n\n"
                                    f"You've been invited to join the project '{project.title}'.\n"
                                    "Please log in to your account to accept the invitation.\n\n"
                                    "Best regards,\nYour Team"
                                ),
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user.email],
                                fail_silently=True
                            )

                        # Create notification for the invited student
                        student = Student.objects.filter(user=user).first()
                        if student:
                            Notification.objects.create(
                                student=student,
                                project=project,
                                message=f"You have been invited to join the project '{project.title}'."
                            )

            messages.success(
                request,
                f"Project '{project.title}' created successfully! Invited {invited_count} user(s)."
            )
            return redirect('dashboard:collab')

        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            return redirect('dashboard:collab')

    # GET request handling
    categories = Categories.objects.all()
    skills = Skill.objects.all()
    return render(request, 'add_project.html', {
        'categories': categories,
        'skills': skills,
    })


# Removed @login_required for testing


@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        access_type = request.POST.get('privacy')
        category_ids = request.POST.getlist('categories')

        try:
            categories = Categories.objects.filter(id__in=category_ids)

            project.title = title
            project.description = description
            project.access_type = access_type
            project.save()
            project.categories.set(categories)

            messages.success(request, 'Project updated successfully!')
            return redirect('dashboard:project_detail', project_id=project.id)
        except Exception as e:
            messages.error(request, f'Error updating project: {str(e)}')

    categories = Categories.objects.all()
    return render(request, 'update_project.html', {
        'project': project,
        'categories': categories,
        'privacy_choices': Project.ACCESS_TYPE
    })


# Delete project view


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if project.owner != request.user:
            return HttpResponseForbidden("You are not allowed to delete this project.")

        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('dashboard:collab')

    return render(request, 'delete_project.html', {
        'project': project
    })


# Join Project view


@login_required
def join_project_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        # Try to join project using your existing method
        if project.join_project(request.user):
            messages.success(
                request, "🎉 You've successfully joined the project!")
            return redirect('dashboard:project_detail', project_id=project.id)
        else:
            # Handle failure reasons for join
            if project.access_type == 'invite' and request.user not in project.invited_users.all():
                messages.warning(
                    request, "❌ You need an invitation to join this project.")
            elif project.members.count() >= project.max_members:
                messages.error(request, "⚠️ This project is already full.")
            else:
                messages.error(
                    request, "🚫 You're not allowed to join this project.")
            return redirect('dashboard:project_detail', project_id=project.id)

    # GET request → Show confirmation page
    return render(request, 'join_project.html', {
        'project': project,
    })


@login_required
@require_POST
def join_project_ajax(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Check if user already joined
    if project.members.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'You are already a member.'}, status=400)

    # Check invitation if required
    if project.access_type == 'invite' and request.user not in project.invited_users.all():
        return JsonResponse({'error': 'You need an invitation to join this project.'}, status=403)

    # Check max members
    if project.members.count() >= project.max_members:
        return JsonResponse({'error': 'Project is full.'}, status=400)

    if project.join_project(request.user):
        return JsonResponse({'success': "🎉 You've successfully joined the project!"})
    else:
        return JsonResponse({'error': 'Failed to join project.'}, status=400)


# leave Project view


@login_required
def leave_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        if request.user not in project.members.all():
            return HttpResponseForbidden("You are not a member of this project.")

        project.members.remove(request.user)
        messages.success(request, 'You have left the project successfully!')
        return redirect('dashboard:collab')

    # GET request => show confirmation page
    return render(request, 'leave_project.html', {
        'project': project
    })


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    members_without_owner = project.members.exclude(id=project.owner.id)

    assignable_user_ids = list(project.members.values_list(
        'id', flat=True)) + list(project.invited_users.values_list('id', flat=True))
    assignable_users = User.objects.filter(
        id__in=assignable_user_ids).distinct()

    tasks = project.tasks.select_related('assigned_to')

    task_form = TaskForm(assignable_users=assignable_users)

    if request.method == 'POST':
        if 'add_task' in request.POST:
            task_form = TaskForm(
                request.POST, assignable_users=assignable_users)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.project = project
                task.save()
                return redirect('dashboard:project_detail', project_id=project.id)

    return render(request, 'project_detail.html', {
        'project': project,
        'tasks': tasks,
        'task_form': task_form,
        'members': project.members.all(),
        'members_without_owner': members_without_owner,
    })


@login_required
def toggle_task_complete(request):
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        is_completed = data.get('is_completed')

        task = get_object_or_404(Task, id=task_id)

        # Authorization check
        if task.assigned_to != request.user:
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)

        task.is_completed = is_completed
        task.save()

        # Calculate progress for the project
        project = task.project
        total = project.tasks.count()
        completed = project.tasks.filter(is_completed=True).count()
        progress = int((completed / total) * 100) if total > 0 else 0

        return JsonResponse({
            'success': True,
            'is_completed': task.is_completed,
            'progress': progress,
            'completed_tasks': completed,
            'total_tasks': total,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

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
