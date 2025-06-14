
from django.shortcuts import redirect
from django.urls import reverse
from .models import Student

class EnsureProfileCompleteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            if request.path not in [reverse('account:edit_profile'), reverse('account:logout')]:
                student = Student.objects.filter(user=request.user).first()
                if student and not student.is_profile_complete():
                    return redirect('account:edit_profile')

        return self.get_response(request)
