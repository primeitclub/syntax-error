from django.urls import path
from . import views

app_name = 'connections'

urlpatterns = [
    path('send/<int:to_user_id>/', views.send_connection_request, name='send_connection_request'),
    path('respond/<int:request_id>/<str:action>/', views.respond_connection_request, name='respond_connection_request'),
    path('requests/', views.list_connection_requests, name='list_connection_requests'),
    path('connected_list/', views.connected_list, name='connected_list'),
    path('delete/<int:user_id>/', views.delete_connection, name='delete_connection'),
    path('profile/<int:user_id>/', views.view_other_profile, name='view_profile'),
]
