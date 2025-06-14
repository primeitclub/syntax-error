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
# 
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'registration/login.html', {'error': 'Email not found'})

        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid password'})

    return render(request, 'registration/login.html')

# Registration view to handle user registration
def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'registration/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(email=email).exists():
            return render(request, 'registration/register.html', {'error': 'Email already registered'})

        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = False 
        user.save()

        Student.objects.create(user=user, username=username, email=email)

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)  

        EmailOTP.objects.update_or_create(
            user=user,
            defaults={'otp': otp_code, 'expires_at': expires_at}
        )

        # Send OTP email
        send_mail(
            subject="Your OTP Code",
            message=f"Hello {first_name},\nYour OTP code is {otp_code}. It will expire in 10 minutes.",
            from_email="Employee Management System <hamrohr.webapp@gmail.com>",
            recipient_list=[email],
        )

        # Save user id in session to verify OTP later
        request.session['pending_user_id'] = user.id

        return redirect('verify_otp')

    return render(request, 'registration/register.html')


# Logout view to handle user logout
def logout_view(request):
    logout(request)
    return redirect('login')
