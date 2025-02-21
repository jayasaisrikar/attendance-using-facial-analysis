from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20)
    branch = models.CharField(max_length=50)
    year = models.IntegerField()
    course = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to='profile_images/students/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.roll_number}"

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)
    employee_id = models.CharField(max_length=20)
    profile_image = models.ImageField(upload_to='profile_images/faculty/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.department}"