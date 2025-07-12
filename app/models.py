from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
# from ckeditor.fields import RichTextField
# from ckeditor_uploader.fields import RichTextUploadingField
import uuid

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'pk': self.pk})

class Question(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    image = models.ImageField(upload_to='question_images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    tags = models.ManyToManyField(Tag, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    vote_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('question_detail', kwargs={'pk': self.pk})
    
    @property
    def answer_count(self):
        return self.answers.filter(is_active=True).count()

    @property
    def has_accepted_answer(self):
        return self.answers.filter(is_accepted=True).exists()

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(default=False)
    vote_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-is_accepted', '-created_at']
    
    def __str__(self):
        if self.question:
            return f"Answer to: {self.question.title}"
        elif self.parent:
            return f"Reply to: {self.parent.content[:50]}..."
        else:
            return f"Answer by {self.author.username}"
    
    @property
    def is_reply(self):
        return self.parent is not None
    
    @property
    def is_main_answer(self):
        return self.question is not None and self.parent is None
    
    @property
    def is_comment(self):
        return self.question is not None and self.parent is not None
    
    @property
    def root_answer(self):
        """Get the top-level answer in the thread"""
        if self.parent:
            return self.parent.root_answer
        return self
    
    @property
    def depth(self):
        """Get the depth level of this answer in the thread"""
        if self.parent:
            return self.parent.depth + 1
        return 0
    
    @property
    def reply_count(self):
        """Get the number of direct replies"""
        return self.replies.filter(is_active=True).count()
    
    @property
    def all_replies(self):
        """Get all replies recursively"""
        replies = []
        for reply in self.replies.filter(is_active=True):
            replies.append(reply)
            replies.extend(reply.all_replies)
        return replies

class UserVote(models.Model):
    VOTE_CHOICES = [
        (1, 'Upvote'),
        (-1, 'Downvote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.IntegerField(choices=VOTE_CHOICES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ('user', 'question'),
            ('user', 'answer')
        ]

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('answer', 'New Answer'),
        ('comment', 'New Comment'),
        ('mention', 'Mention'),
        ('vote', 'Vote'),
        ('accept', 'Answer Accepted'),
        ('follow', 'New Follower'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    target_url = models.CharField(max_length=500, blank=True)  # URL to navigate to when clicked
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"
    
    def get_target_url(self):
        """Generate target URL based on notification type"""
        if self.target_url:
            return self.target_url
        
        if self.notification_type in ['answer', 'comment', 'mention', 'accept'] and self.question:
            if self.answer:
                return f"{self.question.get_absolute_url()}#answer-{self.answer.id}"
            return self.question.get_absolute_url()
        elif self.notification_type == 'follow' and self.sender:
            return self.sender.profile.get_absolute_url()
        elif self.notification_type == 'vote' and self.question:
            return self.question.get_absolute_url()
        
        return '#'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    background_image = models.ImageField(upload_to='backgrounds/', null=True, blank=True)
    reputation = models.IntegerField(default=0)
    is_banned = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Follow relationships
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})
    
    @property
    def follower_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.user.following.count()
    
    def is_following(self, user):
        return user in self.followers.all()
    
    def follow(self, user_to_follow):
        if user_to_follow != self.user:
            self.followers.add(user_to_follow)
            return True
        return False
    
    def unfollow(self, user_to_unfollow):
        self.followers.remove(user_to_unfollow)
        return True

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# Signal to update last_login in UserProfile when user logs in
@receiver(post_save, sender=User)
def update_user_profile_last_login(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        # Update last_login in UserProfile when User.last_login changes
        if instance.last_login:
            instance.profile.last_login = instance.last_login
            instance.profile.save(update_fields=['last_login'])
