from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard,name="dashboard"),
    path('feed/',views.feed,name="feed"),
    path('group/',views.group,name="group"),
    path('collab/',views.dashboard,name="collab"),
    path('inbox/',views.dashboard,name="inbox"),
    path('notification/',views.dashboard,name="notification"),
]
