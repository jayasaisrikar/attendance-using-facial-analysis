from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('signup/faculty/', views.faculty_signup, name='faculty_signup'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/timetable/', views.manage_timetable, name='manage_timetable'),
    path('admin/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('view-timetable/', views.view_timetable, name='view_timetable'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('faculty/records/', views.view_records, name='view_records'),
    path('faculty/timetable/', views.manage_timetable, name='manage_timetable'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
] 