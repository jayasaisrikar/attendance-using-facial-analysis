from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, Faculty

class StudentRegistrationForm(UserCreationForm):
    roll_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    branch = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    course = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Add image fields dynamically
        for i in range(1, 16):
            field_name = f'image_{i}'
            self.fields[field_name] = forms.ImageField(
                required=False,
                widget=forms.FileInput(attrs={
                    'class': 'form-control',
                    'accept': 'image/*'
                })
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
            student = Student.objects.create(
                user=user,
                roll_number=self.cleaned_data.get('roll_number'),
                branch=self.cleaned_data.get('branch'),
                year=self.cleaned_data.get('year'),
                course=self.cleaned_data.get('course')
            )
        return user

class FacultyRegistrationForm(UserCreationForm):
    department = forms.CharField(max_length=50)
    employee_id = forms.CharField(max_length=20)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_faculty = True
        if commit:
            user.save()
            Faculty.objects.create(
                user=user,
                department=self.cleaned_data.get('department'),
                employee_id=self.cleaned_data.get('employee_id')
            )
        return user