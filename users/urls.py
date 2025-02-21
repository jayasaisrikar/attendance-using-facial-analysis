from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/register/', views.student_register, name='student_register'),
    path('faculty/register/', views.faculty_register, name='faculty_register'),
    
    # Admin URLs - moved from admin/ to manage/ to avoid conflict with Django admin
    path('manage/pending/', views.pending_approvals, name='pending_approvals'),
    path('manage/users/', views.user_list, name='user_list'),
    path('manage/approve/student/<int:pk>/', views.approve_student, name='approve_student'),
    path('manage/reject/student/<int:pk>/', views.reject_student, name='reject_student'),
    path('manage/approve/faculty/<int:pk>/', views.approve_faculty, name='approve_faculty'),
    path('manage/reject/faculty/<int:pk>/', views.reject_faculty, name='reject_faculty'),
    path('my-account/', views.my_account, name='my_account'),
]