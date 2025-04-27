from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Category

@receiver(post_save, sender=User)
def create_premade_categories_for_user(sender, instance, created, **kwargs):
    if created:
        # When a new user is created, create premade categories for this user
        Category.create_premade_categories(user=instance)
