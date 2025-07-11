from django.urls import path
from . import views
app_name = 'dashboard'  
urlpatterns = [

    path('',views.feed,name="feed"),
    
    path('collab/',views.collab,name="collab"),
    path('notifications/', views.notification, name='notification'),
    path('notifications/dismiss/', views.dismiss_notifications, name='dismiss_notifications'),
    path('notifications/detail/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    # path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.add_project, name='add_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/update/', views.update_project, name='update_project'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('projects/<int:project_id>/leave/', views.leave_project, name='leave_project'),
    path('projects/<int:project_id>/join/', views.join_project_view, name='join_project'),
    path('projects/<int:project_id>/join/ajax/', views.join_project_ajax, name='join_project_ajax'),
    path('tasks/<int:task_id>/toggle_complete/', views.toggle_task_completion, name='toggle_task_completion')



]