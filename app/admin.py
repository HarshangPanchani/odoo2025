from django.contrib import admin
from django.utils.html import format_html
from .models import Question, Answer, Tag, UserVote, Notification, UserProfile

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'question_count']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'views', 'answer_count', 'vote_count', 'is_active']
    list_filter = ['is_active', 'created_at', 'tags']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['views', 'created_at', 'updated_at']
    filter_horizontal = ['tags']
    ordering = ['-created_at']
    
    def answer_count(self, obj):
        return obj.answer_count
    answer_count.short_description = 'Answers'
    
    def vote_count(self, obj):
        return obj.vote_count
    vote_count.short_description = 'Votes'

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'author', 'created_at', 'is_accepted', 'vote_count', 'is_active']
    list_filter = ['is_accepted', 'is_active', 'created_at']
    search_fields = ['content', 'author__username', 'question__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def vote_count(self, obj):
        return obj.vote_count
    vote_count.short_description = 'Votes'

@admin.register(UserVote)
class UserVoteAdmin(admin.ModelAdmin):
    list_display = ['question', 'user', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['question__title', 'user__username']
    ordering = ['-created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'sender', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'reputation', 'is_premium', 'is_banned', 'follower_count', 'last_login', 'created_at']
    list_filter = ['is_premium', 'is_banned', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']
    readonly_fields = ['reputation', 'follower_count', 'following_count', 'created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'avatar', 'background_image')
        }),
        ('Status', {
            'fields': ('is_premium', 'is_banned', 'reputation')
        }),
        ('Activity', {
            'fields': ('last_login', 'created_at')
        }),
        ('Follow Relationships', {
            'fields': ('followers',),
            'classes': ('collapse',)
        }),
    )
    
    def follower_count(self, obj):
        return obj.follower_count
    follower_count.short_description = 'Followers'
    
    def following_count(self, obj):
        return obj.following_count
    following_count.short_description = 'Following'
