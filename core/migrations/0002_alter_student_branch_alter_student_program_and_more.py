# Generated by Django 4.1.13 on 2024-12-30 16:17

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='branch',
            field=models.CharField(choices=[('CSE', 'Computer Science'), ('ECE', 'Electronics'), ('ME', 'Mechanical'), ('CE', 'Civil'), ('IT', 'Information Technology')], max_length=50),
        ),
        migrations.AlterField(
            model_name='student',
            name='program',
            field=models.CharField(choices=[('B.Tech', 'B.Tech'), ('M.Tech', 'M.Tech'), ('MBA', 'MBA')], max_length=50),
        ),
        migrations.AlterField(
            model_name='student',
            name='year',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)]),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='branch',
            field=models.CharField(choices=[('CSE', 'Computer Science'), ('ECE', 'Electronics'), ('ME', 'Mechanical'), ('CE', 'Civil'), ('IT', 'Information Technology')], max_length=50),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='day',
            field=models.CharField(choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday')], max_length=10),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='period',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)]),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='program',
            field=models.CharField(choices=[('B.Tech', 'B.Tech'), ('M.Tech', 'M.Tech'), ('MBA', 'MBA')], max_length=50),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='year',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)]),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('student', 'Student'), ('faculty', 'Faculty'), ('admin', 'Admin')], max_length=10),
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[('LOGIN', 'User Login'), ('LOGOUT', 'User Logout'), ('ATTENDANCE', 'Attendance Marked'), ('REGISTRATION', 'New Registration'), ('APPROVAL', 'User Approval'), ('TIMETABLE', 'Timetable Update'), ('SYSTEM', 'System Activity')], max_length=20)),
                ('description', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
