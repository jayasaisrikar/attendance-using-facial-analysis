from django.db import models
from users.models import Faculty

class TimeTable(models.Model):
    DAYS_OF_WEEK = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
    ]

    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    time_slot = models.CharField(max_length=50)
    branch = models.CharField(max_length=50)
    year = models.IntegerField()
    course = models.CharField(max_length=50)

    class Meta:
        unique_together = ['faculty', 'day', 'time_slot']

    def __str__(self):
        return f"{self.subject} - {self.day} - {self.time_slot}"