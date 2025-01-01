from django.core.management.base import BaseCommand
from core.models import TimeTable, Faculty, User

class Command(BaseCommand):
    help = 'Creates sample timetable entries for faculty'

    def handle(self, *args, **kwargs):
        # Get the first faculty user
        try:
            faculty = Faculty.objects.first()
            if not faculty:
                self.stdout.write(self.style.ERROR('No faculty found. Please create a faculty user first.'))
                return
            
            # Sample timetable data
            timetable_data = [
                # Monday
                {'day': 'Monday', 'period': 1, 'subject': 'Python Programming', 'program': 'B.Tech', 'branch': 'CSE', 'year': 1},
                {'day': 'Monday', 'period': 2, 'subject': 'Data Structures', 'program': 'B.Tech', 'branch': 'CSE', 'year': 2},
                {'day': 'Monday', 'period': 3, 'subject': 'Database Systems', 'program': 'B.Tech', 'branch': 'CSE', 'year': 3},
                
                # Tuesday
                {'day': 'Tuesday', 'period': 1, 'subject': 'Web Development', 'program': 'B.Tech', 'branch': 'CSE', 'year': 2},
                {'day': 'Tuesday', 'period': 2, 'subject': 'Machine Learning', 'program': 'B.Tech', 'branch': 'CSE', 'year': 3},
                
                # Add more entries as needed
            ]
            
            # Create timetable entries
            for data in timetable_data:
                TimeTable.objects.get_or_create(
                    faculty=faculty,
                    day=data['day'],
                    period=data['period'],
                    subject=data['subject'],
                    program=data['program'],
                    branch=data['branch'],
                    year=data['year']
                )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created timetable entries for {faculty.user.email}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating timetable: {str(e)}')) 