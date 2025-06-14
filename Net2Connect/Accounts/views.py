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
from .models import EmailOTP


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
                return redirect('/dashboard')
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

        return redirect('verify_otp')

    return render(request, 'registration/register.html')


# Logout view to handle user logout
def logout_view(request):
    logout(request)
    return redirect('account:login')


def profile(request):
    student = Student.objects.filter(user=request.user).first()
    student.last_active = timezone.now()
    points = student.points
    if points < 0:
        student.points = 0
    return render(request, 'profile.html', {'student': student})


@login_required
def editprofile(request):
    student = Student.objects.filter(user=request.user).first()

    if request.method == 'POST':
        address = request.POST.get('address')
        website = request.POST.get('website')  # field name in template
        github = request.POST.get('github')
        linkedin = request.POST.get('linkedin')  # field name in template

        student.address = address
        student.website_url = website
        student.github_url = github
        student.linkedin_url = linkedin
        student.save()

        return redirect('account:profile')

    return render(request, 'editprofile.html', {
        'student': student,
        'user': request.user,  # to access user.email
        'profile': {
            'avatar_url': None  # you can dynamically fetch an avatar later
        }
    })
