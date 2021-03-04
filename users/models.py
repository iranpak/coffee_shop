from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history import register


class User(AbstractUser):
    first_name = models.CharField(max_length=64, null=False)
    last_name = models.CharField(max_length=64, null=False)
    email = models.EmailField(unique=True, null=False)


register(User)
