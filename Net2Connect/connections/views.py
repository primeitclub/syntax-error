from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from .models import ConnectionRequest
from Accounts.models import Student


# 🔄 Send Connection Request
@login_required
def send_connection_request(request, to_user_id):
    to_user = get_object_or_404(User, id=to_user_id)
    from_user = request.user

    if to_user == from_user:
        return JsonResponse({'error': "Can't connect to yourself"}, status=400)

    if ConnectionRequest.objects.filter(
        Q(from_user=from_user, to_user=to_user) |
        Q(from_user=to_user, to_user=from_user, accepted=True)
    ).exists():
        return JsonResponse({'error': "Request already sent or already connected"}, status=400)

    ConnectionRequest.objects.create(from_user=from_user, to_user=to_user)
    return JsonResponse({'success': "Connection request sent."})


# 🔄 View All Incoming Requests
@login_required
def list_connection_requests(request):
    pending_requests = ConnectionRequest.objects.filter(
        to_user=request.user, accepted__isnull=True)
    return render(request, 'requests.html', {'requests': pending_requests})


# 🔄 Respond to Connection Request
@login_required
def respond_connection_request(request, request_id, action):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    conn_req = get_object_or_404(ConnectionRequest, id=request_id, to_user=request.user)

    if action == 'accept':
        conn_req.accepted = True
        conn_req.save()

        from_student = get_object_or_404(Student, user=conn_req.from_user)
        to_student = get_object_or_404(Student, user=conn_req.to_user)

        from_student.connections.add(to_student)
        to_student.connections.add(from_student)

        return JsonResponse({'success': "Connection accepted."})

    elif action == 'reject':
        conn_req.accepted = False
        conn_req.save()
        return JsonResponse({'success': "Connection rejected."})

    return JsonResponse({'error': "Invalid action."}, status=400)


# 🔄 Connected Users List
@login_required
def connected_list(request):
    student = get_object_or_404(Student, user=request.user)
    connections = student.connections.all()
    return render(request, 'connected_list.html', {'connections': connections})


# 🔄 Delete/Remove Connection
@login_required
def delete_connection(request, user_id):
    if request.method == "POST":
        current_student = get_object_or_404(Student, user=request.user)
        other_student = get_object_or_404(Student, user__id=user_id)

        current_student.connections.remove(other_student)
        other_student.connections.remove(current_student)

        return redirect('connections:connected_list')

    return JsonResponse({'error': 'Invalid request'}, status=400)


# 🔎 View Public Profile of Another Student
@login_required
def view_other_profile(request, user_id):
    student = get_object_or_404(Student, user__id=user_id)
    return render(request, 'view_other_profile.html', {'student': student})
