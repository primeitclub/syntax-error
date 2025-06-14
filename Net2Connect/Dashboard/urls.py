from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',views.dashboard,name="dashboard"),
    path('feed/',views.feed,name="feed"),
    path('group/',views.group,name="group"),
    path('collab/',views.collab,name="collab"),
    path('inbox/',views.inbox,name="inbox"),
    path('notification/',views.notification,name="notification"),
]
