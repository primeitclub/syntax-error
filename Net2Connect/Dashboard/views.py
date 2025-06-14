from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request,'dashboard.html')

def feed(request):
    return render(request,'feed.html')

def collab(request):
    return render(request,'collab.html')

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