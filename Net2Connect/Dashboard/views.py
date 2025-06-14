from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
# Create your views here.
@login_required(login_url='/')
def home_view(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You are not allowed to access this page.")
    return render(request, 'home.html')
