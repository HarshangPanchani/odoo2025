from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from app.models import Question, Answer, User, UserProfile, Tag
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

@login_required
@staff_member_required
def dashboard(request):
    """Main moderation dashboard"""
    # Get statistics
    total_questions = Question.objects.count()
    total_answers = Answer.objects.count()
    total_users = User.objects.count()
    total_tags = Tag.objects.count()
    recent_questions = Question.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    recent_answers = Answer.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    
    # Get recent content for moderation
    recent_questions_list = Question.objects.select_related('author').order_by('-created_at')[:10]
    recent_answers_list = Answer.objects.select_related('author', 'question').order_by('-created_at')[:10]
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:10]
    
    context = {
        'total_questions': total_questions,
        'total_answers': total_answers,
        'total_users': total_users,
        'total_tags': total_tags,
        'recent_questions': recent_questions,
        'recent_answers': recent_answers,
        'recent_questions_list': recent_questions_list,
        'recent_answers_list': recent_answers_list,
        'recent_users': recent_users,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@staff_member_required
def questions_list(request):
    """List all questions for moderation"""
    questions = Question.objects.select_related('author').prefetch_related('tags').order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        questions = questions.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(author__username__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        questions = questions.filter(is_active=True)
    elif status == 'inactive':
        questions = questions.filter(is_active=False)
    
    context = {
        'questions': questions,
        'search': search,
        'status': status,
    }
    return render(request, 'admin_panel/questions_list.html', context)

@login_required
@staff_member_required
def answers_list(request):
    """List all answers for moderation"""
    answers = Answer.objects.select_related('author', 'question').order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        answers = answers.filter(
            Q(content__icontains=search) |
            Q(author__username__icontains=search) |
            Q(question__title__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        answers = answers.filter(is_active=True)
    elif status == 'inactive':
        answers = answers.filter(is_active=False)
    
    context = {
        'answers': answers,
        'search': search,
        'status': status,
    }
    return render(request, 'admin_panel/answers_list.html', context)

@login_required
@staff_member_required
def users_list(request):
    """List all users for moderation"""
    users = User.objects.select_related('profile').annotate(
        question_count=Count('questions'),
        answer_count=Count('answers')
    ).order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'banned':
        users = users.filter(profile__is_banned=True)
    
    context = {
        'users': users,
        'search': search,
        'status': status,
    }
    return render(request, 'admin_panel/users_list.html', context)

@login_required
@staff_member_required
def tags_list(request):
    """List all tags for management"""
    tags = Tag.objects.annotate(
        question_count=Count('questions')
    ).order_by('name')
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        tags = tags.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'tags': tags,
        'search': search,
    }
    return render(request, 'admin_panel/tags_list.html', context)

# Moderation Actions
@require_POST
@login_required
@staff_member_required
def delete_question(request, question_id):
    """Delete a question"""
    question = get_object_or_404(Question, id=question_id)
    question_title = question.title
    question.delete()
    messages.success(request, f'Question "{question_title}" has been deleted.')
    return redirect('admin_panel:questions_list')

@require_POST
@login_required
@staff_member_required
def toggle_question_status(request, question_id):
    """Toggle question active/inactive status"""
    question = get_object_or_404(Question, id=question_id)
    question.is_active = not question.is_active
    question.save()
    status = 'activated' if question.is_active else 'deactivated'
    messages.success(request, f'Question "{question.title}" has been {status}.')
    return redirect('admin_panel:questions_list')

@require_POST
@login_required
@staff_member_required
def delete_answer(request, answer_id):
    """Delete an answer"""
    answer = get_object_or_404(Answer, id=answer_id)
    answer_content = answer.content[:50] + "..." if len(answer.content) > 50 else answer.content
    answer.delete()
    messages.success(request, f'Answer "{answer_content}" has been deleted.')
    return redirect('admin_panel:answers_list')

@require_POST
@login_required
@staff_member_required
def toggle_answer_status(request, answer_id):
    """Toggle answer active/inactive status with hierarchical handling"""
    answer = get_object_or_404(Answer, id=answer_id)
    
    if not answer.is_active:
        # Activating - just activate this answer
        answer.is_active = True
        answer.save()
        status = 'activated'
        messages.success(request, f'Answer has been {status}.')
    else:
        # Deactivating - handle hierarchical comments
        answer.is_active = False
        answer.save()
        
        # Deactivate all child comments recursively
        def deactivate_children(parent_answer):
            children = Answer.objects.filter(parent=parent_answer, is_active=True)
            for child in children:
                child.is_active = False
                child.save()
                deactivate_children(child)
        
        deactivate_children(answer)
        
        # Count how many children were deactivated
        child_count = Answer.objects.filter(parent=answer).count()
        
        if child_count > 0:
            status = 'deactivated'
            messages.success(request, f'Answer and {child_count} reply(ies) have been {status} and hidden from view.')
        else:
            status = 'deactivated'
            messages.success(request, f'Answer has been {status} and hidden from view.')
    
    return redirect('admin_panel:answers_list')

@require_POST
@login_required
@staff_member_required
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" has been {status}.')
    return redirect('admin_panel:users_list')

@require_POST
@login_required
@staff_member_required
def toggle_user_ban(request, user_id):
    """Toggle user ban status"""
    user = get_object_or_404(User, id=user_id)
    if hasattr(user, 'profile'):
        user.profile.is_banned = not user.profile.is_banned
        user.profile.save()
        status = 'banned' if user.profile.is_banned else 'unbanned'
        messages.success(request, f'User "{user.username}" has been {status}.')
    return redirect('admin_panel:users_list')

# Tag Management Actions
@require_POST
@login_required
@staff_member_required
def create_tag(request):
    """Create a new tag"""
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not name:
        messages.error(request, 'Tag name is required.')
        return redirect('admin_panel:tags_list')
    
    # Check if tag already exists
    if Tag.objects.filter(name__iexact=name).exists():
        messages.error(request, f'Tag "{name}" already exists.')
        return redirect('admin_panel:tags_list')
    
    Tag.objects.create(name=name, description=description)
    messages.success(request, f'Tag "{name}" has been created.')
    return redirect('admin_panel:tags_list')

@require_POST
@login_required
@staff_member_required
def delete_tag(request, tag_id):
    """Delete a tag"""
    tag = get_object_or_404(Tag, id=tag_id)
    tag_name = tag.name
    tag.delete()
    messages.success(request, f'Tag "{tag_name}" has been deleted.')
    return redirect('admin_panel:tags_list')

@require_POST
@login_required
@staff_member_required
def edit_tag(request, tag_id):
    """Edit a tag"""
    tag = get_object_or_404(Tag, id=tag_id)
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not name:
        messages.error(request, 'Tag name is required.')
        return redirect('admin_panel:tags_list')
    
    # Check if name conflicts with existing tag
    existing_tag = Tag.objects.filter(name__iexact=name).exclude(id=tag_id).first()
    if existing_tag:
        messages.error(request, f'Tag "{name}" already exists.')
        return redirect('admin_panel:tags_list')
    
    tag.name = name
    tag.description = description
    tag.save()
    messages.success(request, f'Tag "{name}" has been updated.')
    return redirect('admin_panel:tags_list')
