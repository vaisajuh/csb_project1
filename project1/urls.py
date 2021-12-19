from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('validate/', views.validate_view, name='validate'),
    path('logout/', views.logout_view, name='logout'),
    path('todo/', views.todo_view, name='todo'),
    path('addBird/', views.register_bird_view, name='addBird'),
    path('getBird/', views.get_bird_view, name="getBird"),
    path('forum/', views.forum_view, name="forum"),
]