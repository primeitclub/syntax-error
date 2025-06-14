from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student, EmailOTP
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Student
from .otp_verify import verify_otp_view
import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from .models import EmailOTP, Skill

# login_view


def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            error = 'Email not found'
        else:
            user = authenticate(
                request, username=user.username, password=password)
            # print(f"User active status: {user.is_active}")
            if user is not None:

                login(request, user)
                return redirect('/dashboard/feed')
            else:
                error = 'Invalid password'

    return render(request, 'registration/login.html', {'error': error})


# Registration view to handle user registration

def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Password mismatch
        if password != confirm_password:
            return render(request, 'registration/register.html', {
                'error': 'Passwords do not match',
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
            })

        # Email already registered
        if User.objects.filter(email=email).exists():
            return render(request, 'registration/register.html', {
                'error': 'Email is already registered',
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
            })

        # Create a unique username
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Create inactive user
        user = User.objects.create_user(
            username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = False
        user.save()

        # Create Student profile
        Student.objects.create(user=user, user_name=username, email=email)

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)
        print(f"Generated OTP: {otp_code} for user: {user.username}")
        EmailOTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp_code, 'expires_at': expires_at}
        )

        # Send OTP via email
        send_mail(
            subject="Your OTP Code for Hamro HR",
            message=f"Hello {first_name},\n\nYour OTP code is: {otp_code}\n\nIt will expire in 10 minutes.\n\nThank you!",
            from_email="Net2Connect <hamrohr.webapp@gmail.com>",
            recipient_list=[email],
            fail_silently=False
        )

        # Save user ID in session
        request.session['pending_user_id'] = user.id

        return redirect('account:verify_otp')

    return render(request, 'registration/register.html')


# Logout view to handle user logout
def logout_view(request):
    logout(request)
    return redirect('account:login')


def profile(request):
    student = Student.objects.filter(user=request.user).first()
    student.last_active = timezone.now()

    if student.points < 0:
        student.points = 0

    student.save()

    return render(request, 'profile.html', {
        'student': student,
    })


@login_required
def editprofile(request):
    # Try to get the Student instance; if none, raise 404 or handle accordingly
    student = get_object_or_404(Student, user=request.user)
    all_skills = Skill.objects.all()

    if request.method == 'POST':
        address = request.POST.get('address')
        website = request.POST.get('website')  # match form field name
        github = request.POST.get('github')
        linkedin = request.POST.get('linkedin')
        description = request.POST.get('description')
        interest_fields = request.POST.get('interest_fields')
        skills_ids = request.POST.getlist(
            'skills')  # list of skill IDs as strings

        student.address = address
        student.website_url = website
        student.github_url = github
        student.linkedin_url = linkedin
        student.description = description
        student.interest_fields = interest_fields

        skills_ids = request.POST.getlist('skills')  # existing skill IDs
        new_skills_raw = request.POST.get(
            'new_skills', '')  # comma separated string

    # Fetch existing skills by ID
        skills_objs = list(Skill.objects.filter(id__in=skills_ids))

        # Process new skills if any
        if new_skills_raw:
            # Split by comma, strip spaces, ignore empty strings
            new_skill_names = [name.strip()
                               for name in new_skills_raw.split(',') if name.strip()]

            # For each new skill name, check if it exists, if not create
            for skill_name in new_skill_names:
                skill_obj, created = Skill.objects.get_or_create(
                    name__iexact=skill_name, defaults={'name': skill_name})
                skills_objs.append(skill_obj)

        # Set all skills (existing + new) to student
        student.skills.set(skills_objs)

        # Save student
        student.save()
        return redirect('account:profile')

    # Assuming Student model has an avatar field or user profile does:
    avatar_url = None
    if hasattr(student, 'avatar') and student.avatar:
        avatar_url = student.avatar.url
    # Or customize according to your model

    context = {
        'student': student,
        'user': request.user,
        'profile': {
            'avatar_url': avatar_url,
        },
        'all_skills': all_skills,
    }
    return render(request, 'editprofile.html', context)
