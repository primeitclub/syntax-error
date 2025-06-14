from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from Accounts.models import Student

@login_required(login_url='/')  
def home_view(request):
    student_data = Student.objects.filter(user=request.user).first()

    if not student_data:
        return HttpResponse("Student profile not found. Please contact admin.", status=404)

    context = {
        'student': student_data
    }
    return render(request, 'home.html', context)
