from django import forms
from django.utils import timezone
from .models import JobListing
class JobForm(forms.ModelForm):
    class Meta:
        model = JobListing
        fields = ['title','description','required_skills','location','job_type','deadline','status']
        widgets = {
            'description':forms.Textarea(attrs={'rows':5}),
            'required_skills':forms.Textarea(attrs={'rows':3}),
            'deadline':forms.DateInput(attrs={'type':'date'}),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now().date():
            raise forms.ValidationError('Deadline cannot be in the past.')
        return deadline
