from django.urls import path
from . import views
from connections.views import view_other_profile
app_name='account'
urlpatterns = [
    path('',views.login_view, name='login'),
    path('profile/<str:username>/', views.profile, name='my_profile'),
  # for logged-in user
    path('profile/<str:username>/', view_other_profile, name='profile'),  # for others

    path('register/',views.register_view, name='register'),
    path('verify_otp/', views.verify_otp_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.editprofile, name='edit_profile')
]
