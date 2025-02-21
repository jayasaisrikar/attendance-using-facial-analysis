from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Attendance, ClassPhoto
from .serializers import (
    AttendanceSerializer, 
    ClassPhotoSerializer,
    AttendanceReportSerializer
)

class AttendanceViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttendanceSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student:
            return Attendance.objects.filter(student=user.student)
        elif user.is_faculty:
            return Attendance.objects.filter(faculty=user.faculty)
        return Attendance.objects.all()
        
    @action(detail=False, methods=['post'])
    def bulk_mark(self, request):
        students = request.data.get('students', [])
        subject = request.data.get('subject')
        date = request.data.get('date')
        
        created_attendance = []
        for student_id in students:
            attendance = Attendance.objects.create(
                student_id=student_id,
                faculty=request.user.faculty,
                subject=subject,
                date=date,
                is_present=True
            )
            created_attendance.append(attendance)
            
        serializer = self.get_serializer(created_attendance, many=True)
        return Response(serializer.data)