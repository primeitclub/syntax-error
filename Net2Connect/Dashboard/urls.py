from django.urls import path
from . import views
app_name = 'dashboard'  
urlpatterns = [

    path('',views.feed,name="feed"),
    
    path('collab/',views.collab,name="collab"),
    path('inbox/',views.dashboard,name="inbox"),
    path('notification/',views.dashboard,name="notification"),
    # path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/update/', views.update_project, name='update_project'),
]


