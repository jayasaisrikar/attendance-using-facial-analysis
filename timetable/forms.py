from django import forms
from .models import TimeTable

class TimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = ['subject', 'day', 'time_slot', 'branch', 'year', 'course']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-control'}),
            'time_slot': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control'}),
        }