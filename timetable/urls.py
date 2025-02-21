from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('view/', views.view_timetable, name='view_timetable'),
    path('manage/', views.manage_timetable, name='manage_timetable'),
    path('edit/<int:pk>/', views.edit_timetable, name='edit_timetable'),
    path('delete/<int:pk>/', views.delete_timetable, name='delete_timetable'),
]