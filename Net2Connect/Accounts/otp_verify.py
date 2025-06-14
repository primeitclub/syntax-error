from .models import EmailOTP
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def verify_otp_view(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp', '').strip()

        user_id = request.session.get('pending_user_id')
        if not user_id:
            return redirect('register')  

        try:
            user = User.objects.get(id=user_id)
            otp_record = EmailOTP.objects.get(user=user)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return render(request, 'registration/verify_otp.html', {'error': 'Invalid session or OTP record not found'})

        if otp_record.is_expired():
            otp_record.delete()
            return render(request, 'registration/verify_otp.html', {'error': 'OTP expired. Please register again.'})

        if otp_record.otp == otp_input:
            # Activate account and login
            user.is_active = True
            user.save()
            login(request, user)

            # Clean up
            otp_record.delete()
            request.session.pop('pending_user_id', None)

            return redirect('dashboard:home')
        else:
            return render(request, 'registration/verify_otp.html', {'error': 'Invalid OTP'})

    return render(request, 'registration/verify_otp.html')
