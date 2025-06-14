from .models import EmailOTP
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


def verify_otp_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip().lower()
        otp_input = request.POST.get('otp').strip()

        try:
            user = User.objects.get(email=email)
            otp_record = EmailOTP.objects.get(user=user)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return render(request, 'registration/verify_otp.html', {'error': 'Invalid email or OTP'})

        if otp_record.is_expired():
            otp_record.delete()
            return render(request, 'registration/verify_otp.html', {'error': 'OTP expired. Please register again.'})

        if otp_record.otp == otp_input:
            # OTP valid, log user in, delete OTP record
            login(request, user)
            otp_record.delete()
            return redirect('home')  
        else:
            return render(request, 'registration/verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'registration/verify_otp.html')
