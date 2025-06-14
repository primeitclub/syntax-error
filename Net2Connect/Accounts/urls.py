from django.urls import path
from . import views

urlpatterns = [
    path('',views.login_view, name='login'),
    path('profile/',views.profile,name="profile"),
    path('editprofile/',views.editprofile,name="editprofile"),
]
