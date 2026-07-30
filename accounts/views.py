from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import StudentRegForm, EmployerRegForm, StudentProfileForm, EmployerProfileForm
from .models import CustomUser, StudentProfile, EmployerProfile, SKILL_OPTIONS

def home(request):
    if request.user.is_authenticated: return redirect('dashboard')
    return render(request, 'accounts/home.html')

def register_choice(request):
    return render(request, 'accounts/register_choice.html')

def register_student(request):
    form = StudentRegForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = 'student'; user.email = form.cleaned_data['email']; user.save()
        StudentProfile.objects.create(user=user, department=form.cleaned_data['department'],
            level=form.cleaned_data['level'], skills=form.cleaned_data['skills'],
            phone=form.cleaned_data.get('phone',''), cv=form.cleaned_data.get('cv'))
        login(request, user)
        messages.success(request, f'Welcome {user.first_name}! Your account is ready.')
        return redirect('dashboard')
    return render(request, 'accounts/register_student.html', {'form': form, 'skill_options': SKILL_OPTIONS})

def register_employer(request):
    form = EmployerRegForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.role = 'employer'; user.email = form.cleaned_data['email']; user.save()
        EmployerProfile.objects.create(user=user, company_name=form.cleaned_data['company_name'],
            company_email=form.cleaned_data['company_email'], industry=form.cleaned_data['industry'],
            company_description=form.cleaned_data.get('company_description',''),
            website=form.cleaned_data['website'], location=form.cleaned_data.get('location',''))
        login(request, user)
        messages.success(request, f'Welcome! {form.cleaned_data["company_name"]} is registered.')
        return redirect('dashboard')
    return render(request, 'accounts/register_employer.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('dashboard')
    identifier = ''
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        user_obj = CustomUser.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier)).first()
        user = authenticate(request, username=user_obj.username, password=password) if user_obj else None
        if user: login(request, user); return redirect('dashboard')
        messages.error(request, 'Invalid username/email or password.')
    return render(request, 'accounts/login.html', {'identifier': identifier})

def logout_view(request):
    logout(request); return redirect('home')

@login_required
def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        request.user.profile_picture = request.FILES['profile_picture']
        request.user.save()
        messages.success(request, 'Profile picture updated!')
    return redirect('profile')

@login_required
def profile(request):
    user = request.user
    if user.is_student():
        p = getattr(user, 'student_profile', None)
        form = StudentProfileForm(request.POST or None, request.FILES or None, instance=p)
        if request.method == 'POST' and form.is_valid():
            form.save(); messages.success(request, 'Profile updated!'); return redirect('profile')
        return render(request, 'accounts/profile_student.html', {'form':form,'profile':p,'skill_options':SKILL_OPTIONS})
    elif user.is_employer():
        p = getattr(user, 'employer_profile', None)
        form = EmployerProfileForm(request.POST or None, instance=p)
        if request.method == 'POST' and form.is_valid():
            form.save(); messages.success(request, 'Profile updated!'); return redirect('profile')
        return render(request, 'accounts/profile_employer.html', {'form':form,'profile':p})
    return redirect('dashboard')
