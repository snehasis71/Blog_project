from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

# all the URLs
urlpatterns = [
    path('home/', views.home, name='home'),
    path ('create/', views.create_post, name ='create_post'),
    path ('edit/<int:id>', views.edit_post, name='edit_post'),
    path ('delete/<int:id>', views.delete_post, name='delete_post'),
    path ('dashboard/', views.dashboard, name='dashboard'), 
    path ('post/<int:post_id>/', views.post_details, name='post_details'), 
    
    
    # Authentication URLs
    path('signup/', views.signup, name='signup'),      # <-- signup path
    path ('', views.login_view, name='login'),   # <-- Login path
    path ('logout/', views.logout_view, name='logout'), # <-- Logout path
    
    #Likes dislikes
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),

]

