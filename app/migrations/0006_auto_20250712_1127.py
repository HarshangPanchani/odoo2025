# Generated by Django 5.2.4 on 2025-07-12 11:27

from django.db import migrations

def create_user_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('app', 'UserProfile')
    
    # Create profiles for users who don't have one
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)

def reverse_create_user_profiles(apps, schema_editor):
    # No reverse operation needed
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_notification_target_url_question_image_and_more'),
    ]

    operations = [
        migrations.RunPython(create_user_profiles, reverse_create_user_profiles),
    ]
