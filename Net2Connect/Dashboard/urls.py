from django.urls import path
from . import views
app_name = 'dashboard'  
urlpatterns = [

    path('', views.home_view, name='home'),
    path('feed/',views.feed,name="feed"),
    path('group/',views.group,name="group"),
    path('collab/',views.collab,name="collab"),
    path('inbox/',views.dashboard,name="inbox"),
    path('notification/',views.dashboard,name="notification"),
    # path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.add_project, name='add_project'),
    path('project/', views.collabs_view, name='project_detail'),
    path('projects/<int:project_id>/update/', views.update_project, name='update_project'),
   
]


