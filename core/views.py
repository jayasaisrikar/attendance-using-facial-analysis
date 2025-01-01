import tempfile
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CommonChoices, User, Student, Faculty, TimeTable, Attendance, ActivityLog
from .forms import StudentSignUpForm, FacultySignUpForm, TimeTableForm
from face_recognition.utils import FaceRecognitionUtil
import os
from .analytics import AttendanceAnalytics
from face_recognition.enhanced_utils import EnhancedFaceRecognition
from django.conf import settings
from django.db import models
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.utils import IntegrityError
from django.utils import timezone
from django.db.models import Q

def home(request):
    return render(request, 'home.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"Login attempt with email: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"Found user: {user.email}, type: {user.user_type}")
            
            authenticated_user = authenticate(request, email=email, password=password)
            print(f"Authentication result: {authenticated_user}")
            
            if authenticated_user is not None:
                if not authenticated_user.is_approved:
                    messages.error(request, 'Your account is pending approval.')
                    return render(request, 'auth/login.html')
                
                login(request, authenticated_user)
                print(f"User logged in: {authenticated_user.email}, type: {authenticated_user.user_type}")
                
                # Simplified redirect logic
                if authenticated_user.is_superuser:
                    return redirect('admin_dashboard')
                elif authenticated_user.user_type == 'student':
                    return redirect('student_dashboard')
                elif authenticated_user.user_type == 'faculty':
                    return redirect('faculty_dashboard')
                
            else:
                messages.error(request, 'Invalid password.')
                
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            
    return render(request, 'auth/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def faculty_signup(request):
    if request.method == 'POST':
        form = FacultySignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.user_type = 'faculty'
            user.is_approved = False
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            Faculty.objects.create(
                user=user,
                department=form.cleaned_data['department']
            )
            
            messages.success(
                request, 
                'Registration successful! Please wait for admin approval before logging in.'
            )
            return redirect('login')
    else:
        form = FacultySignUpForm()
    return render(request, 'auth/faculty_signup.html', {'form': form})

@login_required
def faculty_dashboard(request):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied. Only faculty can access this dashboard.')
        return redirect('home')
    
    try:
        faculty = request.user.faculty
        print(f"Faculty found: {faculty.user.email}")
        all_timetables = TimeTable.objects.filter(faculty=faculty)
        print(f"Total timetable entries for faculty: {all_timetables.count()}")
        if all_timetables.exists():
            print("Sample timetable entry:", all_timetables.first().__dict__)
    except:
        messages.error(request, 'Faculty profile not found.')
        return redirect('home')
    
    recognized_students = []
    
    # Basic options for all faculties
    programs = ['B.Tech', 'M.Tech', 'MBA']
    branches = ['CSE', 'ECE', 'ME', 'CE']
    years = range(1, 5)
    
    # Get selected filters
    selected_program = request.GET.get('program')
    selected_branch = request.GET.get('branch')
    selected_year = request.GET.get('year')
    selected_day = request.GET.get('day')
    
    # Filter subjects based on selection
    subjects = []
    if all([selected_program, selected_branch, selected_year, selected_day]):
        print(f"Filtering subjects with exact values:")
        print(f"Day: '{selected_day}', Program: '{selected_program}', Branch: '{selected_branch}', Year: {selected_year}")
        print(f"Types - Day: {type(selected_day)}, Program: {type(selected_program)}, Branch: {type(selected_branch)}, Year: {type(selected_year)}")
        
        subjects = TimeTable.objects.filter(
            faculty=faculty,
            program=selected_program,
            branch=selected_branch,
            year=int(selected_year),
            day=selected_day
        ).order_by('period')
        
        print("SQL Query:", subjects.query)
        print(f"Found subjects: {subjects.count()}")
    
    # Handle attendance submission
    if request.method == 'POST' and 'classroom_image' in request.FILES:
        try:
            image_file = request.FILES['classroom_image']
            subject = request.POST.get('subject')
            
            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Process image and get recognized students
            fr_util = EnhancedFaceRecognition()
            recognized_ids = fr_util.process_image(temp_path)
            
            # Get recognized students
            recognized_students = Student.objects.filter(
                roll_number__in=[str(rec.get('student_id')) for rec in recognized_ids]
            )
            
            # Mark attendance
            students = Student.objects.filter(
                program=selected_program,
                branch=selected_branch,
                year=int(selected_year)
            )
            
            for student in students:
                is_present = any(str(student.roll_number) == str(rec.get('student_id')) 
                               for rec in recognized_ids)
                Attendance.objects.create(
                    student=student,
                    subject=subject,
                    is_present=is_present,
                    date=timezone.now().date()
                )
            
            messages.success(request, f'Attendance marked for {len(recognized_students)} students')
            os.unlink(temp_path)
            
        except Exception as e:
            messages.error(request, f'Error processing attendance: {str(e)}')
    
    context = {
        'programs': [choice[0] for choice in CommonChoices.PROGRAM_CHOICES],
        'branches': [choice[0] for choice in CommonChoices.BRANCH_CHOICES],
        'years': [choice[0] for choice in CommonChoices.YEAR_CHOICES],
        'days_of_week': [choice[0] for choice in CommonChoices.DAY_CHOICES],
        'subjects': subjects,
        'recognized_students': recognized_students,
        'selected_filters': {
            'program': selected_program,
            'branch': selected_branch,
            'year': selected_year,
            'day': selected_day
        }
    }
    
    return render(request, 'faculty/dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get current stats
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    active_students = Student.objects.filter(user__is_active=True).count()
    active_faculty = Faculty.objects.filter(user__is_active=True).count()
    
    # Today's stats
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(date=today).count()
    today_classes = TimeTable.objects.filter(day=today.strftime('%A')).count()
    
    # Pending approvals
    pending_approvals = User.objects.filter(is_approved=False).count()
    recent_approvals = User.objects.filter(
        is_approved=False,
        date_joined__gte=timezone.now() - timedelta(days=1)
    ).count()
    
    # Recent activities
    recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:10]
    
    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'active_students': active_students,
        'active_faculty': active_faculty,
        'today_attendance': today_attendance,
        'today_classes': today_classes,
        'pending_approvals': pending_approvals,
        'recent_approvals': recent_approvals,
        'recent_activities': recent_activities,
        'pending_approvals_list': User.objects.filter(is_approved=False).order_by('-date_joined')
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
def approve_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        user = User.objects.get(id=user_id)
        user.is_approved = True
        user.save()
        messages.success(request, f'{user.get_user_type_display()} approved successfully.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('admin_dashboard')

@login_required
def reject_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        user = User.objects.get(id=user_id)
        user.delete()  # Or set some rejection flag if you want to keep records
        messages.success(request, f'{user.get_user_type_display()} rejected successfully.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('admin_dashboard')

@login_required
def manage_timetable(request):
    # Allow both faculty and superuser to access timetable management
    if not (request.user.is_superuser or request.user.user_type == 'faculty'):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # For superuser, show all timetables
    if request.user.is_superuser:
        timetable = TimeTable.objects.all().order_by('day', 'period')
    else:
        # For faculty, show only their timetables
        faculty = request.user.faculty
        timetable = TimeTable.objects.filter(faculty=faculty).order_by('day', 'period')
    
    if request.method == 'POST':
        form = TimeTableForm(request.POST)
        if form.is_valid():
            timetable_entry = form.save(commit=False)
            if not request.user.is_superuser:
                timetable_entry.faculty = request.user.faculty
            timetable_entry.save()
            messages.success(request, 'Timetable entry added successfully.')
            return redirect('manage_timetable')
    else:
        form = TimeTableForm()
    
    context = {
        'timetable': timetable,
        'form': form,
        'is_admin': request.user.is_superuser
    }
    return render(request, 'admin/timetable.html', context)

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            try:
                # Check if roll number already exists
                roll_number = form.cleaned_data['roll_number']
                if Student.objects.filter(roll_number=roll_number).exists():
                    messages.error(request, 'This roll number is already registered.')
                    return render(request, 'auth/student_signup.html', {'form': form})
                
                # Create user
                user = form.save(commit=False)
                user.user_type = 'student'
                user.is_approved = False
                user.save()
                
                # Create student
                student = Student.objects.create(
                    user=user,
                    roll_number=roll_number,
                    program=form.cleaned_data['program'],
                    branch=form.cleaned_data['branch'],
                    year=int(form.cleaned_data['year'])
                )
                
                # Handle face images
                face_images = request.FILES.getlist('face_images[]')
                if face_images:
                    try:
                        # Create directory structure
                        base_path = os.path.join(settings.BASE_DIR, 'media')
                        os.makedirs(base_path, exist_ok=True)
                        
                        student_images_path = os.path.join(base_path, 'student_images')
                        os.makedirs(student_images_path, exist_ok=True)
                        
                        # Use roll number for folder name
                        student_folder = os.path.join(student_images_path, str(roll_number))
                        os.makedirs(student_folder, exist_ok=True)
                        
                        print(f"Created folder structure at: {student_folder}")
                        
                        # Save captured images
                        for i, image_data in enumerate(face_images):
                            image_path = os.path.join(student_folder, f'face_{i}.jpg')
                            with open(image_path, 'wb+') as destination:
                                for chunk in image_data.chunks():
                                    destination.write(chunk)
                            print(f"Saved image {i+1} at: {image_path}")
                        
                        # Train model
                        fr_util = EnhancedFaceRecognition()
                        fr_util.load_or_train_model()
                        print(f"Model trained for student with roll number: {roll_number}")
                        
                    except Exception as e:
                        print(f"Error saving images: {str(e)}")
                        messages.error(request, 'Error saving face images. Please try again.')
                        user.delete()
                        return redirect('student_signup')
                else:
                    print("No face images received")
                    messages.error(request, 'Face images are required.')
                    user.delete()
                    return redirect('student_signup')
                
                messages.success(request, 'Registration successful! Please wait for admin approval.')
                return redirect('login')
                
            except IntegrityError as e:
                print(f"Database error: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
                return render(request, 'auth/student_signup.html', {'form': form})
                
    else:
        form = StudentSignUpForm()
    
    return render(request, 'auth/student_signup.html', {'form': form})

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied. Only students can access this dashboard.')
        return redirect('home')
    
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return redirect('home')
    
    # Get timetable
    timetable = TimeTable.objects.filter(
        program=student.program,
        branch=student.branch,
        year=student.year
    ).order_by('day', 'period')
    
    # Group timetable by days
    timetable_by_day = {}
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    periods = range(1, 6)  # Periods 1 to 5
    
    for day in days:
        timetable_by_day[day] = []
        day_entries = timetable.filter(day=day).order_by('period')
        timetable_by_day[day].extend(day_entries)
    
    # Get attendance statistics
    from .analytics import AttendanceAnalytics
    
    # Get overall attendance percentage
    attendance_percentage = AttendanceAnalytics.get_student_attendance_percentage(student.id)
    
    # Get total classes and attended classes
    total_classes = Attendance.objects.filter(student=student).count()
    classes_attended = Attendance.objects.filter(student=student, is_present=True).count()
    
    # Calculate monthly attendance
    this_month = datetime.now().replace(day=1)
    monthly_attendance = Attendance.objects.filter(
        student=student,
        is_present=True,
        date__gte=this_month
    ).count()
    
    # Get subject-wise attendance
    subject_attendance = {}
    for entry in timetable:
        subject = entry.subject
        if subject not in subject_attendance:
            total = Attendance.objects.filter(student=student, subject=subject).count()
            attended = Attendance.objects.filter(student=student, subject=subject, is_present=True).count()
            percentage = (attended / total * 100) if total > 0 else 0
            status = 'Good' if percentage >= 75 else 'Need Improvement'
            
            subject_attendance[subject] = {
                'total': total,
                'attended': attended,
                'percentage': round(percentage, 2),
                'status': status
            }
    
    # Get attendance trend data for chart
    last_30_days = datetime.now() - timedelta(days=30)
    attendance_trend = Attendance.objects.filter(
        student=student,
        date__gte=last_30_days
    ).values('date').annotate(
        present_count=Count('id', filter=Q(is_present=True))
    ).order_by('date')
    
    attendance_dates = [entry['date'].strftime('%Y-%m-%d') for entry in attendance_trend]
    attendance_counts = [entry['present_count'] for entry in attendance_trend]
    
    context = {
        'student': student,
        'total_classes': total_classes,
        'classes_attended': classes_attended,
        'attendance_percentage': round(attendance_percentage, 2),
        'monthly_attendance': monthly_attendance,
        'subject_attendance': subject_attendance,
        'timetable': timetable_by_day,
        'days': days,
        'periods': periods,
        'attendance_dates': attendance_dates,
        'attendance_counts': attendance_counts
    }
    
    return render(request, 'student/dashboard.html', context)

@login_required
def manage_users(request):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    students = Student.objects.select_related('user').all()
    faculty = Faculty.objects.select_related('user').all()
    
    context = {
        'students': students,
        'faculty': faculty
    }
    return render(request, 'admin/manage_users.html', context)

@login_required
def delete_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, 'User deleted successfully.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('manage_users')

@login_required
def view_timetable(request):
    student = Student.objects.get(user=request.user)
    timetable = TimeTable.objects.filter(
        program=student.program,
        branch=student.branch,
        year=student.year
    ).order_by('day', 'period')
    
    context = {
        'timetable': timetable,
    }
    
    return render(request, 'student/timetable.html', context)

@login_required
def attendance_view(request):
    student = Student.objects.get(user=request.user)
    context = {
        'student': student,
    }
    return render(request, 'student/attendance.html', context)

@login_required
def view_records(request):
    if request.user.user_type != 'faculty':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    faculty = request.user.faculty
    
    # Get attendance records for classes taught by this faculty
    attendance_records = Attendance.objects.filter(
        subject__in=TimeTable.objects.filter(faculty=faculty).values_list('subject', flat=True)
    ).select_related('student').order_by('-date')
    
    context = {
        'attendance_records': attendance_records
    }
    return render(request, 'faculty/view_records.html', context)
