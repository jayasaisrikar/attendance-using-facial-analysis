from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    
    def save(self, *args, **kwargs):
        if self.user_type == 'admin':
            self.is_approved = True
            self.is_staff = True
            self.is_superuser = True
        elif self.user_type == 'faculty' and self.is_approved:
            self.is_staff = True
        super().save(*args, **kwargs)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 