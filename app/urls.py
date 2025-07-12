from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('question/<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('ask/', views.ask_question, name='ask_question'),
    
    # Questions and Answers
    path('question/<int:question_id>/answer/', views.post_answer, name='post_answer'),
    path('question/<int:pk>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:pk>/delete/', views.delete_question, name='delete_question'),
    path('answer/<int:pk>/edit/', views.edit_answer, name='edit_answer'),
    path('answer/<int:pk>/delete/', views.delete_answer, name='delete_answer'),
    
    # Voting
    path('question/<int:question_id>/vote/', views.vote_question, name='vote_question'),
    path('answer/<int:answer_id>/vote/', views.vote_answer, name='vote_answer'),
    path('answer/<int:answer_id>/accept/', views.accept_answer, name='accept_answer'),
    
    # User management
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/count/', views.notification_count, name='notification_count'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # Tags
    path('tag/<int:pk>/', views.tag_detail, name='tag_detail'),
    
    # Admin
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/question/<int:question_id>/moderate/', views.admin_moderate_question, name='admin_moderate_question'),
    path('admin/user/<int:user_id>/ban/', views.admin_ban_user, name='admin_ban_user'),
    path('admin/user/<int:user_id>/unban/', views.admin_unban_user, name='admin_unban_user'),
] 