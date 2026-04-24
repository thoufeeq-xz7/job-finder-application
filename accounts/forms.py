from django import forms
from .models import JobApplication, Education

# Form for scheduling interviews
class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['interview_date', 'interview_time', 'meeting_link']
        widgets = {
            'interview_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'interview_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'meeting_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://zoom.us/... or https://meet.google.com/...'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'year']
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
        }
