from django.urls import path
from . import views
app_name='account'
urlpatterns = [
    path('',views.login_view, name='login'),
    path('profile/',views.profile,name="profile"),
    path('register/',views.register_view, name='register'),
    path('verify_otp/', views.verify_otp_view, name='verify_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('edit_profile/', views.editprofile, name='edit_profile')
]
