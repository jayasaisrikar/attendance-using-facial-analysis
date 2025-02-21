from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, FacultyRegistrationForm
from .models import Faculty, Student, User
from attendance.models import Attendance
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from utils.decorators import is_admin, admin_required
from utils.email_utils import send_attendance_notification

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser or user.is_approved:  # Allow superusers to bypass approval check
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is pending approval.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Create directory structure for student images
            student = user.student
            path = f"./media/student_images/{student.course}/{student.branch}/{student.year}/{student.roll_number}"
            os.makedirs(path, exist_ok=True)
            
            # Save all 15 images
            for i in range(1, 16):
                image = form.cleaned_data[f'image_{i}']
                with open(f"{path}/image_{i}.jpg", 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
            
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/student_register.html', {'form': form})

def faculty_register(request):
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('login')
    else:
        form = FacultyRegistrationForm()
    return render(request, 'registration/faculty_register.html', {'form': form})

@login_required
def dashboard(request):
    context = {}
    
    if request.user.is_student:
        recent_attendance = Attendance.objects.filter(
            student=request.user.student
        ).order_by('-date')[:5]
        context['recent_attendance'] = recent_attendance
        return render(request, 'dashboard/student_dashboard.html', context)
    
    elif request.user.is_faculty:
        return render(request, 'dashboard/faculty_dashboard.html')
    
    elif request.user.is_superuser:
        context.update({
            'pending_students': Student.objects.filter(user__is_approved=False),
            'pending_faculty': Faculty.objects.filter(user__is_approved=False),
            'total_students': Student.objects.filter(user__is_approved=True).count(),
            'total_faculty': Faculty.objects.filter(user__is_approved=True).count(),
            'faculty_list': Faculty.objects.filter(user__is_approved=True),
            'student_list': Student.objects.filter(user__is_approved=True)
        })
        return render(request, 'dashboard/admin_dashboard.html', context)
    
    return redirect('login')

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@admin_required
def approve_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.user.is_approved = True
    student.user.save()
    messages.success(request, f'Student {student.user.username} has been approved.')
    return redirect('dashboard')

@admin_required
def reject_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    user = student.user
    student.delete()
    user.delete()
    messages.success(request, f'Student application has been rejected.')
    return redirect('dashboard')

@admin_required
def approve_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty.user.is_approved = True
    faculty.user.save()
    messages.success(request, f'Faculty {faculty.user.username} has been approved.')
    return redirect('dashboard')

@admin_required
def reject_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    user = faculty.user
    faculty.delete()
    user.delete()
    messages.success(request, f'Faculty application has been rejected.')
    return redirect('dashboard')

@admin_required
def pending_approvals(request):
    context = {
        'pending_students': Student.objects.filter(user__is_approved=False),
        'pending_faculty': Faculty.objects.filter(user__is_approved=False)
    }
    return render(request, 'admin/pending_approvals.html', context)

@admin_required
def user_list(request):
    context = {
        'students': Student.objects.filter(user__is_approved=True),
        'faculty': Faculty.objects.filter(user__is_approved=True)
    }
    return render(request, 'admin/user_list.html', context)

@login_required
def my_account(request):
    if request.method == 'POST':
        if 'profile_image' in request.FILES:
            if request.user.is_student:
                student = request.user.student
                student.profile_image = request.FILES['profile_image']
                student.save()
                messages.success(request, 'Profile image updated successfully!')
            elif request.user.is_faculty:
                faculty = request.user.faculty
                faculty.profile_image = request.FILES['profile_image']
                faculty.save()
                messages.success(request, 'Profile image updated successfully!')
        
        # Handle other profile updates
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('my_account')

    return render(request, 'users/my_account.html')