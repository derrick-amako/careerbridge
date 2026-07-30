from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from accounts.models import StudentProfile, EmployerProfile
from jobs.models import JobListing
from applications.models import Application, Recommendation
from ml.matching import save_recommendations

def _is_career_admin(user):
    return user.is_authenticated and (user.is_career_admin() or user.is_staff)

@login_required
def dashboard(request):
    u = request.user
    if u.is_student() and hasattr(u, 'student_profile'): return student_dashboard(request)
    elif u.is_employer() and hasattr(u, 'employer_profile'): return employer_dashboard(request)
    elif u.is_career_admin(): return admin_dashboard(request)
    elif u.is_staff: return redirect('/admin/')
    # Role set but no matching profile (e.g. a student account with no
    # StudentProfile row). redirect('home') would bounce right back here,
    # since home() sends authenticated users to 'dashboard' -- infinite loop.
    logout(request)
    messages.error(request, 'Your account setup is incomplete (no matching profile). Please contact Career Services or register again.')
    return redirect('home')

def student_dashboard(request):
    student = request.user.student_profile
    eligible = student.is_eligible_for_jobs()
    if eligible:
        save_recommendations(student, list(JobListing.objects.filter(status='open', employer__is_verified=True)))
    recs = list(Recommendation.objects.filter(student=student).select_related('job','job__employer')[:5]) if eligible else []
    for rec in recs:
        rec.match_score = rec.compatibility_score  # already the blended score, stored by save_recommendations
    apps = Application.objects.filter(student=student).select_related('job')[:5]
    stats = {
        'total_apps': Application.objects.filter(student=student).count(),
        'shortlisted': Application.objects.filter(student=student, status='shortlisted').count(),
        'open_jobs': JobListing.objects.filter(status='open', employer__is_verified=True).count() if eligible else 0,
        'recommendations': Recommendation.objects.filter(student=student).count() if eligible else 0,
    }
    return render(request, 'dashboard/student.html', {'recommendations':recs,'applications':apps,'stats':stats,'eligible':eligible})

@login_required
def employer_dashboard(request):
    if not request.user.is_employer(): return redirect('dashboard')
    employer = request.user.employer_profile
    jobs = JobListing.objects.filter(employer=employer).annotate(
        app_count=Count('applications'),
        accepted_count=Count('applications', filter=Q(applications__status='accepted')),
    )
    stats = {
        'total_jobs': jobs.count(), 'open_jobs': jobs.filter(status='open').count(),
        'total_apps': Application.objects.filter(job__employer=employer).count(),
        'shortlisted': Application.objects.filter(job__employer=employer, status='shortlisted').count(),
    }
    return render(request, 'dashboard/employer.html', {'jobs':jobs,'stats':stats})

@login_required
def admin_dashboard(request):
    if not _is_career_admin(request.user):
        return redirect('dashboard')
    total_students = StudentProfile.objects.count()
    total_employers = EmployerProfile.objects.count()
    total_jobs = JobListing.objects.count()
    total_apps = Application.objects.count()
    placed = Application.objects.filter(status='accepted').values('student').distinct().count()
    placement_rate = round(placed/total_students*100, 1) if total_students > 0 else 0
    status_data = list(Application.objects.values('status').annotate(count=Count('id')))
    for item in status_data:
        item['pct'] = round(item['count']/total_apps*100) if total_apps > 0 else 0
    context = {
        'total_students':total_students,'total_employers':total_employers,
        'total_jobs':total_jobs,'total_apps':total_apps,'placed':placed,
        'placement_rate':placement_rate,
        'status_data': status_data,
        'job_type_data': list(JobListing.objects.values('job_type').annotate(count=Count('id'))),
        'top_employers': EmployerProfile.objects.annotate(job_count=Count('job_listings')).order_by('-job_count')[:5],
        'recent_apps': Application.objects.select_related('student__user','job').order_by('-date_submitted')[:10],
        'pending_employers': EmployerProfile.objects.filter(is_verified=False, is_rejected=False).select_related('user').order_by('created_at'),
        'rejected_employers': EmployerProfile.objects.filter(is_rejected=True).select_related('user').order_by('-created_at'),
    }
    return render(request, 'dashboard/admin.html', context)

@login_required
def approve_employer(request, pk):
    if not _is_career_admin(request.user):
        return redirect('dashboard')
    employer = get_object_or_404(EmployerProfile, pk=pk)
    if request.method == 'POST':
        employer.is_verified = True
        employer.is_rejected = False
        employer.save(update_fields=['is_verified', 'is_rejected'])
        messages.success(request, f'{employer.company_name} is now verified. Their job postings are visible to students.')
    return redirect('admin_dashboard')

@login_required
def deny_employer(request, pk):
    if not _is_career_admin(request.user):
        return redirect('dashboard')
    employer = get_object_or_404(EmployerProfile, pk=pk)
    if request.method == 'POST':
        employer.is_verified = False
        employer.is_rejected = True
        employer.save(update_fields=['is_verified', 'is_rejected'])
        messages.success(request, f'{employer.company_name} has been denied verification.')
    return redirect('admin_dashboard')
