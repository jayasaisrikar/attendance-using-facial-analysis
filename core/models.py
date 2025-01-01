from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    is_approved = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def clean(self):
        self.username = self.email
        super().clean()

class CommonChoices:
    PROGRAM_CHOICES = [
        ('B.Tech', 'B.Tech'),
        ('M.Tech', 'M.Tech'),
        ('MBA', 'MBA')
    ]
    
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics'),
        ('ME', 'Mechanical'),
        ('CE', 'Civil'),
        ('IT', 'Information Technology')
    ]
    
    YEAR_CHOICES = [(i, i) for i in range(1, 5)]
    
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday')
    ]

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=50, choices=CommonChoices.BRANCH_CHOICES)
    program = models.CharField(max_length=50, choices=CommonChoices.PROGRAM_CHOICES)
    year = models.IntegerField(choices=CommonChoices.YEAR_CHOICES)

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)

class TimeTable(models.Model):
    program = models.CharField(max_length=50, choices=CommonChoices.PROGRAM_CHOICES)
    branch = models.CharField(max_length=50, choices=CommonChoices.BRANCH_CHOICES)
    year = models.IntegerField(choices=CommonChoices.YEAR_CHOICES)
    day = models.CharField(max_length=10, choices=CommonChoices.DAY_CHOICES)
    period = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    subject = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    is_present = models.BooleanField(default=False)
    captured_image = models.ImageField(upload_to='attendance_images/')

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('ATTENDANCE', 'Attendance Marked'),
        ('REGISTRATION', 'New Registration'),
        ('APPROVAL', 'User Approval'),
        ('TIMETABLE', 'Timetable Update'),
        ('SYSTEM', 'System Activity')
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.activity_type} - {self.timestamp}"
