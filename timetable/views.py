from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TimeTable
from .forms import TimeTableForm
from django.http import HttpResponse
import csv
from datetime import datetime
from users.models import Student, Faculty

@login_required
def manage_timetable(request):
    if not request.user.is_faculty:
        return redirect('dashboard')
        
    try:
        faculty = Faculty.objects.get(user=request.user)
        timetable = TimeTable.objects.filter(faculty=faculty).order_by('day', 'time_slot')
        
        if request.method == 'POST':
            day = request.POST.get('day')
            time_slot = request.POST.get('time_slot')
            subject = request.POST.get('subject')
            branch = request.POST.get('branch')
            year = request.POST.get('year')
            course = request.POST.get('course')
            
            # Check if entry already exists
            existing_entry = TimeTable.objects.filter(
                faculty=faculty,
                day=day,
                time_slot=time_slot
            ).first()
            
            if existing_entry:
                messages.error(request, 'You already have a class scheduled for this time slot.')
            else:
                TimeTable.objects.create(
                    faculty=faculty,
                    day=day,
                    time_slot=time_slot,
                    subject=subject,
                    branch=branch,
                    year=year,
                    course=course
                )
                messages.success(request, 'Timetable entry added successfully.')
            
            return redirect('timetable:manage_timetable')
            
        context = {
            'faculty': faculty,
            'timetable': timetable,
            'days': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'],
            'time_slots': [
                '9:00 AM - 10:00 AM',
                '10:00 AM - 11:00 AM',
                '11:00 AM - 12:00 PM',
                '12:00 PM - 1:00 PM',
                '2:00 PM - 3:00 PM',
                '3:00 PM - 4:00 PM',
                '4:00 PM - 5:00 PM'
            ]
        }
        return render(request, 'timetable/manage_timetable.html', context)
        
    except Faculty.DoesNotExist:
        messages.error(request, 'Faculty profile not found.')
        return redirect('dashboard')

@login_required
def view_timetable(request):
    time_slots = [
        '9:00 AM - 10:00 AM',
        '10:00 AM - 11:00 AM',
        '11:00 AM - 12:00 PM',
        '12:00 PM - 1:00 PM',
        '2:00 PM - 3:00 PM',
        '3:00 PM - 4:00 PM',
        '4:00 PM - 5:00 PM'
    ]
    
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_map = dict(zip(days, day_names))
    
    try:
        timetable = None
        context = {}
        
        if request.user.is_student:
            student = Student.objects.get(user=request.user)
            timetable = TimeTable.objects.filter(
                branch=student.branch,
                year=student.year,
                course=student.course
            ).order_by('day', 'time_slot')
            
            context.update({
                'student': student,
                'is_student': True
            })
            
        elif request.user.is_faculty:
            faculty = Faculty.objects.get(user=request.user)
            timetable = TimeTable.objects.filter(
                faculty=faculty
            ).order_by('day', 'time_slot')
            
            context.update({
                'faculty': faculty,
                'is_student': False
            })
            
        elif request.user.is_superuser:
            # For admin, show all timetable entries
            timetable = TimeTable.objects.all().order_by('day', 'time_slot')
            context.update({
                'is_admin': True,
                'is_student': False
            })
        
        if timetable is None:
            messages.error(request, 'Invalid user type')
            return redirect('dashboard')
            
        # Group timetable entries by day
        timetable_by_day = {}
        for day in days:
            timetable_by_day[day_map[day]] = timetable.filter(day=day)
        
        context.update({
            'timetable_by_day': timetable_by_day,
            'days': day_names,
            'time_slots': time_slots
        })
        
        return render(request, 'timetable/view_timetable.html', context)
        
    except (Student.DoesNotExist, Faculty.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')

@login_required
def edit_timetable(request, pk):
    if not request.user.is_faculty:
        return redirect('dashboard')

    timetable = get_object_or_404(TimeTable, pk=pk, faculty=request.user.faculty)
    
    if request.method == 'POST':
        form = TimeTableForm(request.POST, instance=timetable)
        if form.is_valid():
            form.save()
            messages.success(request, 'Timetable entry updated successfully!')
            return redirect('view_timetable')
    else:
        form = TimeTableForm(instance=timetable)

    return render(request, 'timetable/edit_timetable.html', {'form': form})

@login_required
def delete_timetable(request, pk):
    if not request.user.is_faculty:
        return redirect('dashboard')

    timetable = get_object_or_404(TimeTable, pk=pk, faculty=request.user.faculty)
    timetable.delete()
    messages.success(request, 'Timetable entry deleted successfully!')
    return redirect('view_timetable')