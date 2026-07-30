from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Value, CharField
from django.db.models.functions import Replace
from django.http import Http404
from django.utils import timezone
from .models import JobListing
from .forms import JobForm
from applications.models import Application
from accounts.models import SKILL_OPTIONS

def _student_ineligible(request):
    return (request.user.is_authenticated and request.user.is_student()
            and not request.user.student_profile.is_eligible_for_jobs())

def job_list(request):
    if _student_ineligible(request):
        return render(request, 'jobs/ineligible.html')
    jobs = JobListing.objects.filter(status='open', employer__is_verified=True, deadline__gte=timezone.now().date())
    q = request.GET.get('q','').strip(); jt = request.GET.get('type','')
    if q:
        words = q.split()
        # Every word must appear somewhere across title/skills/description
        # (not necessarily all in the same field, and not as one exact phrase).
        word_query = Q()
        for w in words:
            word_query &= (Q(title__icontains=w) | Q(required_skills__icontains=w) | Q(description__icontains=w))
        # Also try the query with spaces removed against those same fields with
        # spaces removed, so a run-together query like "fullstack developer"
        # still finds a title like "Full Stack Developer".
        compact_q = q.replace(' ', '')
        jobs = jobs.annotate(
            title_compact=Replace('title', Value(' '), Value(''), output_field=CharField()),
            skills_compact=Replace('required_skills', Value(' '), Value(''), output_field=CharField()),
            description_compact=Replace('description', Value(' '), Value(''), output_field=CharField()),
        )
        compact_query = (Q(title_compact__icontains=compact_q)
                          | Q(skills_compact__icontains=compact_q)
                          | Q(description_compact__icontains=compact_q))
        jobs = jobs.filter(word_query | compact_query).distinct()
    if jt: jobs = jobs.filter(job_type=jt)
    return render(request, 'jobs/job_list.html', {'jobs':jobs,'query':q,'job_type':jt})

def job_detail(request, pk):
    if _student_ineligible(request):
        return render(request, 'jobs/ineligible.html')
    job = get_object_or_404(JobListing, pk=pk)
    user = request.user
    is_owner = user.is_authenticated and user.is_employer() and hasattr(user, 'employer_profile') and job.employer_id == user.employer_profile.id
    is_admin = user.is_authenticated and (user.is_career_admin() or user.is_staff)
    if not job.employer.is_verified and not is_owner and not is_admin:
        raise Http404
    already_applied = False
    if user.is_authenticated and user.is_student():
        already_applied = Application.objects.filter(student=user.student_profile, job=job).exists()
    return render(request, 'jobs/job_detail.html', {'job':job,'already_applied':already_applied})

@login_required
def post_job(request):
    if not request.user.is_employer():
        messages.error(request, 'Only employers can post jobs.'); return redirect('job_list')
    form = JobForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        job = form.save(commit=False); job.employer = request.user.employer_profile; job.save()
        messages.success(request, f'"{job.title}" posted!'); return redirect('employer_dashboard')
    return render(request, 'jobs/post_job.html', {'form':form,'skill_options':SKILL_OPTIONS})

@login_required
def edit_job(request, pk):
    if not request.user.is_employer():
        messages.error(request, 'Only employers can edit jobs.'); return redirect('job_list')
    job = get_object_or_404(JobListing, pk=pk, employer=request.user.employer_profile)
    form = JobForm(request.POST or None, instance=job)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Job updated!'); return redirect('employer_dashboard')
    return render(request, 'jobs/post_job.html', {'form':form,'editing':True,'job':job,'skill_options':SKILL_OPTIONS})

@login_required
def delete_job(request, pk):
    if not request.user.is_employer():
        messages.error(request, 'Only employers can delete jobs.'); return redirect('job_list')
    job = get_object_or_404(JobListing, pk=pk, employer=request.user.employer_profile)
    if request.method == 'POST': job.delete(); messages.success(request, 'Job deleted.')
    return redirect('employer_dashboard')
