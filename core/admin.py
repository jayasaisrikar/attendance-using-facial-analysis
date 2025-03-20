from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, Student, Faculty, TimeTable, Attendance, ActivityLog
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'user_type', 'approval_status', 'is_staff')
    list_filter = ('user_type', 'is_approved', 'is_staff')
    list_editable = ('is_approved',)
    actions = ['approve_users']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('user_type', 'is_approved', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type', 'is_approved', 'is_staff'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

    def approval_status(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green;">Approved</span>')
        return format_html('<span style="color: red;">Pending</span>')
    approval_status.short_description = 'Approval Status'

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        for obj in queryset:
            if obj.user_type == 'faculty':
                obj.is_staff = True
                obj.save()
    approve_users.short_description = "Approve selected users"

    def save_model(self, request, obj, form, change):
        if obj.user_type == 'faculty' and obj.is_approved:
            obj.is_staff = True
        super().save_model(request, obj, form, change)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'activity_type', 'user', 'description', 'ip_address')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('description', 'user__email')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(TimeTable)
admin.site.register(Attendance)