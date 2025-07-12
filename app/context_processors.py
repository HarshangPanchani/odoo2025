from .models import Tag, Notification

def common_data(request):
    """Add common data to all templates"""
    context = {}
    
    # Add tags for navigation
    context['tags'] = Tag.objects.all()[:20]
    
    # Add notification count for authenticated users
    if request.user.is_authenticated:
        context['unread_notifications_count'] = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
    else:
        context['unread_notifications_count'] = 0
    
    return context 