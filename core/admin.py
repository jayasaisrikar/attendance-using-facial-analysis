from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, Student, Faculty, TimeTable, Attendance, ActivityLog

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'user_type', 'is_approved', 'is_staff')
    list_filter = ('user_type', 'is_approved', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('user_type', 'is_approved', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type', 'is_approved'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'activity_type', 'user', 'description', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('description', 'user__email')
    readonly_fields = ('timestamp', 'ip_address')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(TimeTable)
admin.site.register(Attendance)
