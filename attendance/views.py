from cv2 import FaceRecognizerSF
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Attendance, ClassPhoto, AttendanceAlert
from users.models import Student
from timetable.models import TimeTable
from datetime import datetime, time, timedelta
from django.utils import timezone
from .face_recognition.recognizer import OptimizedFaceRecognizer
import os
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@login_required
def take_attendance(request):
    if not request.user.is_faculty:
        return redirect('dashboard')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        branch = request.POST.get('branch')
        year = request.POST.get('year')
        photo = request.FILES.get('class_photo')

        try:
            # Get all students for this year/branch
            all_students = Student.objects.filter(
                branch=branch,
                year=year,
                user__is_approved=True
            )

            if not all_students.exists():
                messages.warning(request, f'No students found for {branch} year {year}')
                return redirect('view_attendance')

            # Save class photo
            class_photo = ClassPhoto.objects.create(
                faculty=request.user.faculty,
                subject=subject,
                date=datetime.now().date(),
                photo=photo,
                branch=branch,
                year=year
            )

            # Process attendance for present students
            student_images_dir = os.path.join('media', 'student_images')
            if not os.path.exists(student_images_dir):
                messages.warning(request, f"Student images directory not found at: {student_images_dir}")
                return redirect('view_attendance')

            recognizer = OptimizedFaceRecognizer(student_images_dir)
            output_path = class_photo.photo.path.replace('.jpg', '_annotated.jpg')
            recognized_students = recognizer.mark_attendance(class_photo.photo.path, output_path)

            # Mark attendance for all students
            attendance_count = 0
            absent_count = 0
            today = datetime.now().date()
            
            # Get the current time slot based on current time
            current_time = datetime.now().time()
            time_slot = get_current_time_slot(current_time)
            
            # Verify if faculty has class at this time
            if not TimeTable.objects.filter(
                faculty=request.user.faculty,
                day=datetime.now().strftime('%a').upper(),
                time_slot=time_slot,
                year=year,
                branch=branch
            ).exists():
                messages.error(request, 'You do not have a scheduled class at this time.')
                return redirect('view_attendance')

            # Mark attendance for all students
            for student in all_students:
                try:
                    # Check if student was recognized (present)
                    is_present = student.roll_number in recognized_students
                    
                    attendance, created = Attendance.objects.get_or_create(
                        student=student,
                        faculty=request.user.faculty,
                        subject=subject,
                        date=today,
                        defaults={'is_present': is_present}
                    )
                    
                    if created:
                        if is_present:
                            attendance_count += 1
                        else:
                            absent_count += 1
                            
                except Exception as e:
                    messages.warning(request, f"Error marking attendance for {student.roll_number}: {str(e)}")

            class_photo.processed = True
            class_photo.save()

            messages.success(
                request,
                f'Attendance marked: {attendance_count} present, {absent_count} absent'
            )

        except Exception as e:
            messages.error(request, f'Error processing attendance: {str(e)}')

        return redirect('view_attendance')

    return render(request, 'attendance/take_attendance.html')

def get_current_time_slot(current_time):
    time_slots = {
        '9:00 AM - 10:00 AM': (time(9, 0), time(10, 0)),
        '10:00 AM - 11:00 AM': (time(10, 0), time(11, 0)),
        '11:00 AM - 12:00 PM': (time(11, 0), time(12, 0)),
        '12:00 PM - 1:00 PM': (time(12, 0), time(13, 0)),
        '2:00 PM - 3:00 PM': (time(14, 0), time(15, 0)),
        '3:00 PM - 4:00 PM': (time(15, 0), time(16, 0)),
        '4:00 PM - 5:00 PM': (time(16, 0), time(17, 0))
    }
    
    for slot, (start, end) in time_slots.items():
        if start <= current_time <= end:
            return slot
    return None

@login_required
def view_attendance(request):
    context = {}
    if request.user.is_student:
        attendance = Attendance.objects.filter(student=request.user.student)
        context['attendance'] = attendance
    elif request.user.is_faculty:
        attendance = Attendance.objects.filter(faculty=request.user.faculty)
        context['attendance'] = attendance
    
    return render(request, 'attendance/view_attendance.html', context)


from django.http import HttpResponse
import csv
from datetime import datetime, timedelta
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Attendance, ClassPhoto
from users.models import Student
import pandas as pd

@login_required
def attendance_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        subject = request.POST.get('subject')
        
        attendance_data = Attendance.objects.filter(
            date__range=[start_date, end_date]
        )
        
        if subject:
            attendance_data = attendance_data.filter(subject=subject)
            
        if request.user.is_student:
            attendance_data = attendance_data.filter(student=request.user.student)
        elif request.user.is_faculty:
            attendance_data = attendance_data.filter(faculty=request.user.faculty)
            
        # Calculate statistics
        total_classes = attendance_data.values('date', 'subject').distinct().count()
        present_count = attendance_data.filter(is_present=True).count()
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        
        context = {
            'attendance_data': attendance_data,
            'total_classes': total_classes,
            'present_count': present_count,
            'attendance_percentage': round(attendance_percentage, 2)
        }
        
        return render(request, 'attendance/report.html', context)
        
    return render(request, 'attendance/report_form.html')

@login_required
def export_attendance(request):
    if not request.user.is_faculty and not request.user.is_superuser:
        return redirect('dashboard')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Student', 'Subject', 'Status'])
    
    attendance_data = Attendance.objects.all()
    if request.user.is_faculty:
        attendance_data = attendance_data.filter(faculty=request.user.faculty)
        
    for attendance in attendance_data:
        writer.writerow([
            attendance.date,
            attendance.student.roll_number,
            attendance.subject,
            'Present' if attendance.is_present else 'Absent'
        ])
        
    return response

@login_required
def process_attendance(request, photo_id):
    if not request.user.is_faculty:
        return redirect('dashboard')
        
    class_photo = ClassPhoto.objects.get(pk=photo_id)
    
    # Process the class photo using face recognition
    recognizer = FaceRecognizerSF('media/student_images')
    recognized_students = recognizer.recognize_faces(class_photo.photo.path)
    
    # Mark attendance for recognized students
    for student_id in recognized_students:
        student = Student.objects.get(roll_number=student_id)
        Attendance.objects.create(
            student=student,
            faculty=request.user.faculty,
            subject=class_photo.subject,
            date=class_photo.date,
            is_present=True
        )
    
    class_photo.processed = True
    class_photo.save()
    
    return redirect('view_attendance')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Attendance, ClassPhoto
from users.models import Student
from utils.email_utils import send_attendance_notification, send_low_attendance_alert
from utils.statistics import AttendanceAnalytics
from .api.serializers import AttendanceSerializer
from datetime import datetime

@login_required
def attendance_statistics(request):
    if request.user.is_student:
        attendance_data = Attendance.objects.filter(student=request.user.student)
    elif request.user.is_faculty:
        attendance_data = Attendance.objects.filter(faculty=request.user.faculty)
    else:
        attendance_data = Attendance.objects.all()

    analytics = AttendanceAnalytics(attendance_data)
    monthly_stats = analytics.generate_monthly_report()
    subject_stats = analytics.generate_subject_wise_report()
    attendance_graph = analytics.generate_attendance_graph()

    context = {
        'monthly_stats': monthly_stats,
        'subject_stats': subject_stats,
        'attendance_graph': attendance_graph,
        'attendance_data': {
            'months': monthly_stats['month'].tolist(),
            'percentages': monthly_stats['percentage'].tolist(),
            'subjects': subject_stats['subject'].tolist(),
            'subjectPercentages': subject_stats['percentage'].tolist(),
        }
    }

    return render(request, 'attendance/statistics.html', context)

@login_required
def attendance_statistics(request):
    if request.user.is_student:
        attendance_data = Attendance.objects.filter(student=request.user.student)
    elif request.user.is_faculty:
        attendance_data = Attendance.objects.filter(faculty=request.user.faculty)
    else:
        attendance_data = Attendance.objects.all()

    analytics = AttendanceAnalytics(attendance_data)
    
    context = {
        'monthly_stats': analytics.generate_monthly_report(),
        'subject_stats': analytics.generate_subject_wise_report(),
        'attendance_graph': analytics.generate_attendance_graph(),
        'attendance_summary': analytics.get_attendance_summary(),
        'daily_pattern': analytics.get_daily_attendance_pattern(),
        'heatmap': analytics.generate_heatmap()
    }

    if request.GET.get('export'):
        # Export to Excel
        excel_file = analytics.export_to_excel()
        response = HttpResponse(
            excel_file.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=attendance_report.xlsx'
        return response

    return render(request, 'attendance/statistics.html', context)

@login_required
def trigger_attendance_alert(request):
    if not request.user.is_faculty:
        return redirect('dashboard')
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        branch = request.POST.get('branch')
        year = int(request.POST.get('year'))
        duration_minutes = int(request.POST.get('duration', 5))  # Default 5 minutes
        
        # Check if there's already an active alert for this class
        existing_alert = AttendanceAlert.objects.filter(
            faculty=request.user.faculty,
            subject=subject,
            branch=branch,
            year=year,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        
        if existing_alert:
            messages.warning(request, 'An active attendance alert already exists for this class.')
            return redirect('view_attendance')
        
        # Create new alert
        expires_at = timezone.now() + timedelta(minutes=duration_minutes)
        alert = AttendanceAlert.objects.create(
            faculty=request.user.faculty,
            subject=subject,
            branch=branch,
            year=year,
            expires_at=expires_at
        )
        
        messages.success(request, f'Attendance alert triggered! Students have {duration_minutes} minutes to respond.')
        return redirect('view_attendance')
    
    return render(request, 'attendance/trigger_alert.html')

@login_required
def check_alerts(request):
    """API endpoint for students to check if there are any active alerts for them"""
    if not request.user.is_student:
        return JsonResponse({'error': 'Only students can check alerts'}, status=403)
    
    student = request.user.student
    
    # Find active alerts for this student's branch and year
    active_alerts = AttendanceAlert.objects.filter(
        branch=student.branch,
        year=student.year,
        is_active=True,
        expires_at__gt=timezone.now()
    ).order_by('-created_at')
    
    alerts_data = []
    for alert in active_alerts:
        alerts_data.append({
            'id': alert.id,
            'subject': alert.subject,
            'faculty': alert.faculty.user.get_full_name(),
            'expires_at': alert.expires_at.isoformat(),
            'remaining_seconds': int((alert.expires_at - timezone.now()).total_seconds())
        })
    
    return JsonResponse({'alerts': alerts_data})

@csrf_exempt
@login_required
def mark_attendance_from_alert(request):
    """API endpoint for students to mark their attendance from an alert"""
    if not request.user.is_student:
        return JsonResponse({'error': 'Only students can mark attendance'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        alert_id = data.get('alert_id')
        
        alert = AttendanceAlert.objects.get(
            id=alert_id,
            is_active=True,
            expires_at__gt=timezone.now()
        )
        
        # Check if attendance already exists
        existing_attendance = Attendance.objects.filter(
            student=request.user.student,
            faculty=alert.faculty,
            subject=alert.subject,
            date=timezone.now().date()
        ).first()
        
        if existing_attendance:
            messages.warning(request, 'You have already marked your attendance for this class.')
            return JsonResponse({'success': False, 'message': 'Attendance already marked'})
        
        # Mark attendance as present
        Attendance.objects.create(
            student=request.user.student,
            faculty=alert.faculty,
            subject=alert.subject,
            date=timezone.now().date(),
            is_present=True
        )
        
        messages.success(request, 'Attendance marked successfully')
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)