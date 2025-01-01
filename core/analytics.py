from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from .models import Attendance, Student, TimeTable
import pandas as pd

from core import models

class AttendanceAnalytics:
    @staticmethod
    def get_daily_attendance_stats(days=30):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        daily_stats = Attendance.objects.filter(
            date__range=[start_date, end_date]
        ).annotate(
            day=TruncDate('date')
        ).values('day').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(is_present=True))
        ).order_by('day')
        
        return list(daily_stats)

    @staticmethod
    def get_student_attendance_percentage(student_id):
        total = Attendance.objects.filter(student_id=student_id).count()
        present = Attendance.objects.filter(
            student_id=student_id, 
            is_present=True
        ).count()
        
        return (present / total * 100) if total > 0 else 0

    @staticmethod
    def get_subject_wise_attendance(program, branch, year):
        attendance_data = Attendance.objects.filter(
            student__program=program,
            student__branch=branch,
            student__year=year
        ).values('subject').annotate(
            total=Count('id'),
            present=Count('id', filter=Q(is_present=True))
        )
        
        for data in attendance_data:
            data['percentage'] = (data['present'] / data['total'] * 100)
        
        return list(attendance_data)

    @staticmethod
    def generate_attendance_report(start_date, end_date, program=None, branch=None):
        query = Attendance.objects.filter(date__range=[start_date, end_date])
        
        if program:
            query = query.filter(student__program=program)
        if branch:
            query = query.filter(student__branch=branch)
            
        data = query.values(
            'student__roll_number',
            'student__user__username',
            'subject'
        ).annotate(
            total_classes=Count('id'),
            classes_attended=Count('id', filter=models.Q(is_present=True))
        )
        
        df = pd.DataFrame(data)
        df['attendance_percentage'] = (df['classes_attended'] / df['total_classes'] * 100)
        
        return df 

    @staticmethod
    def get_program_wise_stats():
        return Attendance.objects.values(
            'student__program'
        ).annotate(
            total=Count('id'),
            present=Count('id', filter=Q(is_present=True))
        ) 