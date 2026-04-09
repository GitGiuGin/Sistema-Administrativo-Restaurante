from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from decouple import config

@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    User = get_user_model()

    username = settings.SUPERUSER_USERNAME
    password = settings.SUPERUSER_PASSWORD

    if username and password:
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                password=password
            )
            
@receiver(post_migrate)
def create_roles(sender, **kwargs):
    if sender.name != "django.contrib.auth":
        return

    roles = ["Administrador", "Supervisor", "Cajero"]

    for role in roles:
        Group.objects.get_or_create(name=role)