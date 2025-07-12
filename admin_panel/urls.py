from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('questions/', views.questions_list, name='questions_list'),
    path('answers/', views.answers_list, name='answers_list'),
    path('users/', views.users_list, name='users_list'),
    path('tags/', views.tags_list, name='tags_list'),
    
    # Moderation actions
    path('questions/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('questions/<int:question_id>/toggle/', views.toggle_question_status, name='toggle_question_status'),
    path('answers/<int:answer_id>/delete/', views.delete_answer, name='delete_answer'),
    path('answers/<int:answer_id>/toggle/', views.toggle_answer_status, name='toggle_answer_status'),
    path('users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/ban/', views.toggle_user_ban, name='toggle_user_ban'),
    
    # Tag management actions
    path('tags/create/', views.create_tag, name='create_tag'),
    path('tags/<int:tag_id>/delete/', views.delete_tag, name='delete_tag'),
    path('tags/<int:tag_id>/edit/', views.edit_tag, name='edit_tag'),
] 