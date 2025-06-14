from django.urls import path
from . import views

app_name = 'connections'

urlpatterns = [
    path('send/<int:to_user_id>/', views.send_connection_request, name='send_connection_request'),
    path('respond/<int:request_id>/<str:action>/', views.respond_connection_request, name='respond_connection_request'),
]
