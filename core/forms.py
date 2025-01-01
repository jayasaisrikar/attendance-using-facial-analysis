from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TimeTable, User, Student, Faculty

class StudentSignUpForm(forms.ModelForm):
    PROGRAM_CHOICES = [
        ('B.Tech', 'B.Tech'),
        ('M.Tech', 'M.Tech'),
        ('MBA', 'MBA'),
    ]
    
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics'),
        ('ME', 'Mechanical'),
        ('CE', 'Civil'),
    ]

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    roll_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    program = forms.ChoiceField(
        choices=PROGRAM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    branch = forms.ChoiceField(
        choices=BRANCH_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year = forms.ChoiceField(
        choices=[(i, f"Year {i}") for i in range(1, 5)],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.username = self.cleaned_data['email']
        user.user_type = 'student'
        
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                program=self.cleaned_data['program'],
                branch=self.cleaned_data['branch'],
                year=int(self.cleaned_data['year'])
            )
        return user

class FacultySignUpForm(forms.ModelForm):
    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics'),
        ('ME', 'Mechanical'),
        ('CE', 'Civil'),
    ]
    
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'password')

class TimeTableForm(forms.ModelForm):
    PROGRAM_CHOICES = [
        ('B.Tech', 'B.Tech'),
        ('M.Tech', 'M.Tech'),
        ('MBA', 'MBA'),
    ]
    
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics'),
        ('ME', 'Mechanical'),
        ('CE', 'Civil'),
    ]
    
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    program = forms.ChoiceField(choices=PROGRAM_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    branch = forms.ChoiceField(choices=BRANCH_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.ChoiceField(choices=[(i, f"Year {i}") for i in range(1, 5)], widget=forms.Select(attrs={'class': 'form-control'}))
    day = forms.ChoiceField(choices=DAY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    period = forms.ChoiceField(choices=[(i, f"Period {i}") for i in range(1, 6)], widget=forms.Select(attrs={'class': 'form-control'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Faculty"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create fake faculty entries if they don't exist
        fake_faculty = [
            {'name': 'Dr. John Smith', 'email': 'john.smith@example.com', 'dept': 'CSE'},
            {'name': 'Prof. Sarah Johnson', 'email': 'sarah.j@example.com', 'dept': 'ECE'},
            {'name': 'Dr. Michael Brown', 'email': 'michael.b@example.com', 'dept': 'ME'},
            {'name': 'Prof. Emily Davis', 'email': 'emily.d@example.com', 'dept': 'CE'},
        ]
        
        for f in fake_faculty:
            user, _ = User.objects.get_or_create(
                email=f['email'],
                defaults={
                    'username': f['email'],
                    'first_name': f['name'].split()[1],
                    'last_name': f['name'].split()[0],
                    'user_type': 'faculty',
                    'is_approved': True
                }
            )
            Faculty.objects.get_or_create(
                user=user,
                defaults={'department': f['dept']}
            )
        
        self.fields['faculty'].queryset = Faculty.objects.all()

    class Meta:
        model = TimeTable
        fields = ['program', 'branch', 'year', 'day', 'period', 'subject', 'faculty']

    def __str__(self):
        return f"{self.faculty.user.get_full_name()} - {self.subject}" 