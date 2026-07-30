from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, StudentProfile, EmployerProfile
from .validators import validate_real_email

class StudentRegForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(validators=[validate_real_email])
    department = forms.CharField(max_length=200)
    level = forms.ChoiceField(choices=StudentProfile.LEVEL_CHOICES)
    skills = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
    phone = forms.CharField(max_length=20, required=False)
    cv = forms.FileField(required=False)
    class Meta: model = CustomUser; fields = ['username','first_name','last_name','email','password1','password2']

class EmployerRegForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(validators=[validate_real_email])
    company_name = forms.CharField(max_length=200)
    company_email = forms.EmailField(validators=[validate_real_email], help_text="Company contact email, used for verification review")
    industry = forms.CharField(max_length=100)
    company_description = forms.CharField(widget=forms.Textarea(attrs={'rows':3}), required=False)
    website = forms.URLField()
    location = forms.CharField(max_length=200, required=False)
    class Meta: model = CustomUser; fields = ['username','first_name','last_name','email','password1','password2']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['department','level','skills','bio','phone','cv']
        widgets = {'skills':forms.Textarea(attrs={'rows':3}),'bio':forms.Textarea(attrs={'rows':4})}

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = ['company_name','company_email','industry','company_description','website','location','phone']
        widgets = {'company_description':forms.Textarea(attrs={'rows':4})}
