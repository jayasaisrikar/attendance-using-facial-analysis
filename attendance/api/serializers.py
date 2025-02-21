from rest_framework import serializers
from ..models import Attendance, ClassPhoto
from users.models import Student, Faculty

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'branch', 'year', 'course']

class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'department', 'employee_id']

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'faculty', 'subject', 'date', 'is_present', 'timestamp']

class ClassPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPhoto
        fields = ['id', 'faculty', 'subject', 'date', 'photo', 'branch', 'year', 'processed']

class AttendanceReportSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    subject = serializers.CharField(required=False)