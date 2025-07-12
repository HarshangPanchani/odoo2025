from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter
def truncate_words_html(text, num_words):
    """Truncate HTML text to specified number of words"""
    from django.utils.html import strip_tags
    from django.utils.text import Truncator
    
    # Strip HTML tags first
    plain_text = strip_tags(text)
    # Truncate to specified number of words
    truncated = Truncator(plain_text).words(num_words)
    return truncated

@register.simple_tag
def get_user_vote(user, question):
    """Get user's vote for a question"""
    if user.is_authenticated:
        vote = question.votes.filter(user=user).first()
        return vote.vote_type if vote else 0
    return 0

@register.simple_tag
def get_answer_vote(user, answer):
    """Get user's vote for an answer"""
    if user.is_authenticated:
        vote = answer.votes.filter(user=user).first()
        return vote.vote_type if vote else 0
    return 0 

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0 