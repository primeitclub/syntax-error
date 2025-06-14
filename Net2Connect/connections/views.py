from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import ConnectionRequest
from django.contrib.auth.models import User

@login_required
def send_connection_request(request, to_user_id):
    to_user = get_object_or_404(User, id=to_user_id)
    from_user = request.user

    if to_user == from_user:
        return JsonResponse({'error': "Can't connect to yourself"}, status=400)

    # Check if request or accepted connection exists
    if ConnectionRequest.objects.filter(from_user=from_user, to_user=to_user).exists() or \
       ConnectionRequest.objects.filter(from_user=to_user, to_user=from_user, accepted=True).exists():
        return JsonResponse({'error': "Request already sent or already connected"}, status=400)

    ConnectionRequest.objects.create(from_user=from_user, to_user=to_user)
    return JsonResponse({'success': "Connection request sent."})


@login_required
def respond_connection_request(request, request_id, action):
    conn_req = get_object_or_404(ConnectionRequest, id=request_id, to_user=request.user)
    
    if action == 'accept':
        conn_req.accepted = True
        conn_req.save()
        return JsonResponse({'success': "Connection accepted."})
    elif action == 'reject':
        conn_req.accepted = False
        conn_req.save()
        return JsonResponse({'success': "Connection rejected."})
    else:
        return JsonResponse({'error': "Invalid action."}, status=400)
