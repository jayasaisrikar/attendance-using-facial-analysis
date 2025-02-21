from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Faculty

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_student', 'is_faculty', 'is_approved', 'is_staff')
    list_filter = ('is_student', 'is_faculty', 'is_approved')
    fieldsets = UserAdmin.fieldsets + (
        ('User Type', {'fields': ('is_student', 'is_faculty', 'is_approved')}),
    )

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'branch', 'year', 'course')
    search_fields = ('user__username', 'roll_number')
    list_filter = ('branch', 'year', 'course')

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'employee_id')
    search_fields = ('user__username', 'employee_id')
    list_filter = ('department',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
