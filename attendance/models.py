from django.db import models
from users.models import Student, Faculty

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'faculty', 'subject', 'date']

    def __str__(self):
        return f"{self.student.roll_number} - {self.subject} - {self.date}"

class ClassPhoto(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    photo = models.ImageField(upload_to='class_photos/')
    branch = models.CharField(max_length=50)
    year = models.IntegerField()
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.date}"