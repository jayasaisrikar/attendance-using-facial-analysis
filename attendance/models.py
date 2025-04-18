from django.db import models
from users.models import Student, Faculty
from django.utils import timezone

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

# New model for attendance alerts
class AttendanceAlert(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    branch = models.CharField(max_length=50)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    requires_facial_verification = models.BooleanField(default=True)
    attendance_finalized = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.subject} - {self.branch} - Year {self.year}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
        
    def mark_absent_students(self):
        """Mark all students who didn't respond to the alert as absent"""
        from users.models import Student
        
        # Get all students for this branch and year
        students = Student.objects.filter(
            branch=self.branch,
            year=self.year,
            user__is_approved=True
        )
        
        # Count of students marked as absent
        absent_count = 0
        
        # Mark absent students
        for student in students:
            # Check if student already has attendance marked
            existing_attendance = Attendance.objects.filter(
                student=student,
                faculty=self.faculty,
                subject=self.subject,
                date=timezone.now().date()
            ).exists()
            
            if not existing_attendance:
                # Mark as absent
                Attendance.objects.create(
                    student=student,
                    faculty=self.faculty,
                    subject=self.subject,
                    date=timezone.now().date(),
                    is_present=False
                )
                absent_count += 1
        
        # Mark alert as finalized
        self.attendance_finalized = True
        self.save()
        
        return absent_count