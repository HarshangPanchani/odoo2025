from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Question, Answer, Tag, UserVote, Notification, UserProfile
from .forms import QuestionForm, AnswerForm, UserRegistrationForm, UserProfileForm, SearchForm

def home(request):
    """Home page with recent questions"""
    questions = Question.objects.filter(is_active=True).select_related('author').prefetch_related('tags')
    
    # Apply search filters
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        q = search_form.cleaned_data.get('q')
        tags = search_form.cleaned_data.get('tags')
        
        if q:
            questions = questions.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
            )
        
        if tags:
            questions = questions.filter(tags__in=tags).distinct()
    
    # Sort options
    sort = request.GET.get('sort', 'recent')
    if sort == 'popular':
        questions = questions.order_by('-vote_count', '-created_at')
    elif sort == 'unanswered':
        questions = questions.annotate(answer_count=Count('answers')).filter(answer_count=0).order_by('-created_at')
    else:  # recent
        questions = questions.order_by('-created_at')
    
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    selected_tags = request.GET.getlist('tags')
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'sort': sort,
        'tags': Tag.objects.all()[:20],
        'selected_tags': selected_tags,
    }
    return render(request, 'app/home.html', context)

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'app/question_detail.html'
    context_object_name = 'question'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object
        
        # Increment view count
        question.views += 1
        question.save(update_fields=['views'])
        
        # Get user's votes for this question
        user_question_vote = None
        if self.request.user.is_authenticated:
            user_question_vote = UserVote.objects.filter(
                user=self.request.user, 
                question=question
            ).first()
        
        # Get main answers (top-level answers only) with pagination and prefetch replies
        main_answers = question.answers.filter(
            is_active=True, 
            parent=None
        ).select_related('author').prefetch_related(
            'replies__author',
            'replies__replies__author',
            'replies__replies__replies__author'
        ).order_by('-is_accepted', '-created_at')
        
        # Check if user wants to see all comments or just initial 2
        show_all = self.request.GET.get('show_all') == 'true'
        
        if show_all:
            # Show all main answers
            displayed_answers = main_answers
            has_more = False
        else:
            # Show only first 2 main answers
            displayed_answers = main_answers[:2]
            has_more = main_answers.count() > 2
        
        # Get user's votes for displayed answers and their replies
        user_answer_votes = {}
        if self.request.user.is_authenticated:
            # Get all answers that will be displayed (including replies)
            all_displayed_answers = []
            for answer in displayed_answers:
                all_displayed_answers.append(answer)
                # Add all replies recursively
                all_displayed_answers.extend(answer.all_replies)
            
            answer_votes = UserVote.objects.filter(
                user=self.request.user,
                answer__in=all_displayed_answers
            ).select_related('answer')
            for vote in answer_votes:
                user_answer_votes[vote.answer.pk] = vote.vote_type
        
        # Create answer form
        answer_form = AnswerForm()
        
        context.update({
            'user_question_vote': user_question_vote,
            'all_responses': displayed_answers,  # This will be the displayed answers
            'user_answer_votes': user_answer_votes,
            'answer_form': answer_form,
            'has_more_comments': has_more,
            'total_main_answers': main_answers.count(),
            'show_all': show_all,
        })
        
        return context

@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            
            # Handle tags
            tag_names = form.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                question.tags.add(tag)
            
            messages.success(request, 'Question posted successfully!')
            return redirect(question.get_absolute_url())
    else:
        form = QuestionForm()
    
    return render(request, 'app/ask_question.html', {'form': form})

@login_required
def post_answer(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question  # Always set the question first
            answer.author = request.user
            
            # Check if this is a reply to another answer
            parent_id = request.POST.get('parent')
            if parent_id and parent_id.isdigit():
                try:
                    parent_answer = Answer.objects.get(pk=int(parent_id))
                    answer.parent = parent_answer
                    # Ensure the question is set correctly (should already be set above)
                    # But double-check that parent has the same question
                    if parent_answer.question != question:
                        answer.question = parent_answer.question
                except Answer.DoesNotExist:
                    pass  # Invalid parent, treat as main answer
            
            answer.save()
            
            # Create notification for question author (if it's a main answer)
            if not answer.parent and answer.author != question.author:
                Notification.objects.create(
                    recipient=question.author,
                    sender=answer.author,
                    notification_type='answer',
                    question=question,
                    answer=answer,
                    message=f'{answer.author.username} answered your question "{question.title}"'
                )
            
            # Create notification for parent answer author (if it's a reply)
            if answer.parent and answer.author != answer.parent.author:
                Notification.objects.create(
                    recipient=answer.parent.author,
                    sender=answer.author,
                    notification_type='comment',
                    question=question,
                    answer=answer,
                    message=f'{answer.author.username} replied to your answer'
                )
            
            # Create notifications for mentioned users
            content = answer.content
            mentions = [word for word in content.split() if word.startswith('@')]
            for mention in mentions:
                username = mention[1:]  # Remove @
                try:
                    mentioned_user = User.objects.get(username=username)
                    if mentioned_user != answer.author:
                        Notification.objects.create(
                            recipient=mentioned_user,
                            sender=answer.author,
                            notification_type='mention',
                            question=question,
                            answer=answer,
                            message=f'{answer.author.username} mentioned you in a response'
                        )
                except User.DoesNotExist:
                    pass
            
            messages.success(request, 'Response posted successfully!')
            return redirect(question.get_absolute_url())
    
    return redirect(question.get_absolute_url())

@login_required
@require_POST
def vote_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    vote_type = int(request.POST.get('vote_type'))
    
    if vote_type not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    print(f"Processing vote: question={question_id}, user={request.user.id}, vote_type={vote_type}")
    
    # Check if user already voted
    existing_vote = UserVote.objects.filter(user=request.user, question=question).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote
            existing_vote.delete()
            question.vote_count -= vote_type
            question.save()
            vote_type = 0
            print("Vote removed")
        else:
            # Change vote
            old_vote = existing_vote.vote_type
            existing_vote.vote_type = vote_type
            existing_vote.save()
            question.vote_count = question.vote_count - old_vote + vote_type
            question.save()
            print(f"Vote changed from {old_vote} to {vote_type}")
    else:
        # New vote
        UserVote.objects.create(user=request.user, question=question, vote_type=vote_type)
        question.vote_count += vote_type
        question.save()
        print(f"New vote created: {vote_type}")
    
    print(f"Question vote count: {question.vote_count}")
    
    return JsonResponse({
        'vote_count': question.vote_count,
        'user_vote': vote_type
    })

@login_required
@require_POST
def vote_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    vote_type = int(request.POST.get('vote_type'))
    
    if vote_type not in [1, -1]:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    print(f"Processing answer vote: answer={answer_id}, user={request.user.id}, vote_type={vote_type}")
    
    # Check if user already voted
    existing_vote = UserVote.objects.filter(user=request.user, answer=answer).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote
            existing_vote.delete()
            answer.vote_count -= vote_type
            answer.save()
            vote_type = 0
            print("Answer vote removed")
        else:
            # Change vote
            old_vote = existing_vote.vote_type
            existing_vote.vote_type = vote_type
            existing_vote.save()
            answer.vote_count = answer.vote_count - old_vote + vote_type
            answer.save()
            print(f"Answer vote changed from {old_vote} to {vote_type}")
    else:
        # New vote
        UserVote.objects.create(user=request.user, answer=answer, vote_type=vote_type)
        answer.vote_count += vote_type
        answer.save()
        print(f"New answer vote created: {vote_type}")
    
    print(f"Answer vote count: {answer.vote_count}")
    
    return JsonResponse({
        'vote_count': answer.vote_count,
        'user_vote': vote_type
    })

@login_required
@require_POST
def accept_answer(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    question = answer.question
    
    # Only question author can accept answers
    if request.user != question.author:
        return HttpResponseForbidden()
    
    # Unaccept previously accepted answer
    question.answers.filter(is_accepted=True).update(is_accepted=False)
    
    # Accept this answer
    answer.is_accepted = True
    answer.save()
    
    # Create notification for answer author
    Notification.objects.create(
        recipient=answer.author,
        sender=question.author,
        notification_type='accept',
        question=question,
        answer=answer,
        message=f'Your answer to "{question.title}" was accepted!'
    )
    
    return JsonResponse({'success': True})

@login_required
def notifications(request):
    notifications_list = request.user.notifications.all()
    return render(request, 'app/notifications.html', {'notifications': notifications_list})

@login_required
def notification_count(request):
    """Get unread notification count for AJAX requests"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        unread_count = request.user.notifications.filter(is_read=False).count()
        return JsonResponse({'unread_count': unread_count})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.save()
        
        # Get updated unread count
        unread_count = request.user.notifications.filter(is_read=False).count()
        
        # If it's an AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'unread_count': unread_count,
                'notification_id': notification_id
            })
        
        messages.success(request, 'Notification marked as read.')
    
    # Redirect to the target URL if it's a regular request
    target_url = notification.get_target_url()
    return redirect(target_url)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'app/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    questions = user.questions.filter(is_active=True).order_by('-created_at')[:10]
    answers = user.answers.filter(is_active=True).order_by('-created_at')[:10]
    
    # Check if current user is following this user
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = request.user.profile.is_following(user)
    
    return render(request, 'app/profile.html', {
        'profile_user': user,
        'questions': questions,
        'answers': answers,
        'is_following': is_following
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'app/edit_profile.html', {'form': form})

def tag_detail(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    questions = tag.questions.filter(is_active=True).order_by('-created_at')
    
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'app/tag_detail.html', {
        'tag': tag,
        'page_obj': page_obj
    })

@login_required
def edit_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    
    # Only question author can edit
    if request.user != question.author:
        messages.error(request, 'You can only edit your own questions.')
        return redirect(question.get_absolute_url())
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save()
            
            # Handle tags
            question.tags.clear()
            tag_names = form.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.lower())
                question.tags.add(tag)
            
            messages.success(request, 'Question updated successfully!')
            return redirect(question.get_absolute_url())
    else:
        # Pre-populate tags
        initial_tags = ', '.join([tag.name for tag in question.tags.all()])
        form = QuestionForm(instance=question, initial={'tags': initial_tags})
    
    return render(request, 'app/edit_question.html', {'form': form, 'question': question})

@login_required
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    
    # Only question author can delete
    if request.user != question.author:
        messages.error(request, 'You can only delete your own questions.')
        return redirect(question.get_absolute_url())
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('home')
    
    return render(request, 'app/delete_question.html', {'question': question})

@login_required
def edit_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    
    # Only answer author can edit
    if request.user != answer.author:
        messages.error(request, 'You can only edit your own answers.')
        return redirect(answer.question.get_absolute_url())
    
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Answer updated successfully!')
            return redirect(answer.question.get_absolute_url())
    else:
        form = AnswerForm(instance=answer)
    
    return render(request, 'app/edit_answer.html', {'form': form, 'answer': answer})

@login_required
def delete_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    
    # Only answer author can delete
    if request.user != answer.author:
        messages.error(request, 'You can only delete your own answers.')
        return redirect(answer.question.get_absolute_url())
    
    if request.method == 'POST':
        question_url = answer.question.get_absolute_url()
        answer.delete()
        messages.success(request, 'Answer deleted successfully!')
        return redirect(question_url)
    
    return render(request, 'app/delete_answer.html', {'answer': answer})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)
        messages.error(request, 'You cannot follow yourself.')
        return redirect('profile', username=username)
    
    profile = user_to_follow.profile
    current_user_profile = request.user.profile
    
    if current_user_profile.is_following(user_to_follow):
        # Unfollow
        current_user_profile.unfollow(user_to_follow)
        action = 'unfollowed'
        message = f'You unfollowed {username}.'
    else:
        # Follow
        current_user_profile.follow(user_to_follow)
        
        # Create notification
        Notification.objects.create(
            recipient=user_to_follow,
            sender=request.user,
            notification_type='follow',
            message=f'{request.user.username} started following you',
            target_url=request.user.profile.get_absolute_url()
        )
        
        action = 'followed'
        message = f'You are now following {username}.'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'message': message,
            'follower_count': user_to_follow.profile.follower_count
        })
    
    messages.success(request, message)
    return redirect('profile', username=username)

@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.profile.followers.all()
    
    return render(request, 'app/followers_list.html', {
        'profile_user': user,
        'followers': followers,
        'title': f'{username}\'s Followers'
    })

@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    
    # Ensure user has a profile
    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user)
    
    # Get users that this user is following (users who have this user in their followers list)
    following = User.objects.filter(profile__followers=user)
    
    return render(request, 'app/following_list.html', {
        'profile_user': user,
        'following': following,
        'title': f'{username}\'s Following'
    })

# Admin views
@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(ListView):
    model = Question
    template_name = 'app/admin/dashboard.html'
    context_object_name = 'questions'
    
    def get_queryset(self):
        return Question.objects.all().order_by('-created_at')[:20]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['total_questions'] = Question.objects.count()
        context['total_answers'] = Answer.objects.count()
        context['pending_questions'] = Question.objects.filter(is_active=True).count()
        return context

@staff_member_required
def admin_moderate_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            question.is_active = True
            question.save()
            messages.success(request, 'Question approved.')
        elif action == 'reject':
            question.is_active = False
            question.save()
            messages.success(request, 'Question rejected.')
        elif action == 'ban_user':
            question.author.profile.is_banned = True
            question.author.profile.save()
            messages.success(request, 'User banned.')
        
        return redirect('admin_dashboard')
    
    return render(request, 'app/admin/moderate_question.html', {'question': question})

@staff_member_required
def admin_ban_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.profile.is_banned = True
    user.profile.save()
    messages.success(request, f'User {user.username} has been banned.')
    return redirect('admin_dashboard')

@staff_member_required
def admin_unban_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.profile.is_banned = False
    user.profile.save()
    messages.success(request, f'User {user.username} has been unbanned.')
    return redirect('admin_dashboard')
