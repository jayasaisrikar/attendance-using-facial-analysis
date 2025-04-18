from django.core.management.base import BaseCommand
from attendance.models import AttendanceAlert
from django.utils import timezone

class Command(BaseCommand):
    help = 'Process expired attendance alerts and mark absent students'

    def handle(self, *args, **options):
        # Find expired alerts that haven't been finalized
        expired_alerts = AttendanceAlert.objects.filter(
            is_active=True,
            expires_at__lt=timezone.now(),
            attendance_finalized=False
        )
        
        count = 0
        for alert in expired_alerts:
            alert.is_active = False
            alert.mark_absent_students()
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {count} expired alerts')) 