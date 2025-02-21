from django.urls import path
from . import views

urlpatterns = [
    path('take/', views.take_attendance, name='take_attendance'),
    path('view/', views.view_attendance, name='view_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('export/', views.export_attendance, name='export_attendance'),
    path('process/<int:photo_id>/', views.process_attendance, name='process_attendance'),
    path('statistics/', views.attendance_statistics, name='attendance_statistics'),
]