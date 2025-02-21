from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_attendance_notification(student, subject, date, status):
    try:
        subject_line = f"Attendance Marked for {subject}"
        context = {
            'student_name': student.user.get_full_name(),
            'subject': subject,
            'date': date,
            'status': 'Present' if status else 'Absent'
        }
        
        html_message = render_to_string('emails/attendance_notification.html', context)
        
        send_mail(
            subject=subject_line,
            message='',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[student.user.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        logger.error(f"Failed to send attendance notification: {str(e)}")

def send_low_attendance_alert(student, subject, percentage):
    try:
        subject_line = f"Low Attendance Alert - {subject}"
        context = {
            'student_name': student.user.get_full_name(),
            'subject': subject,
            'percentage': percentage
        }
        
        html_message = render_to_string('emails/low_attendance_alert.html', context)
        
        send_mail(
            subject=subject_line,
            message='',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[student.user.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        logger.error(f"Failed to send low attendance alert: {str(e)}")