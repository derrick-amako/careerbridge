import os
import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils import timezone
from jobs.models import JobListing
from .models import Application, Recommendation, StatusHistory, Message
from ml.matching import save_recommendations, compute_skill_gap

def _can_view_application(user, app):
    is_student_owner = user.is_student() and hasattr(user, 'student_profile') and app.student_id == user.student_profile.id
    is_employer_owner = user.is_employer() and hasattr(user, 'employer_profile') and app.job.employer_id == user.employer_profile.id
    return is_student_owner or is_employer_owner

@login_required
def apply_job(request, pk):
    if not request.user.is_student():
        messages.error(request, 'Only students can apply.'); return redirect('job_list')
    job = get_object_or_404(JobListing, pk=pk, status='open', employer__is_verified=True)
    if job.deadline < timezone.now().date():
        messages.error(request, "This job's application deadline has passed.")
        return redirect('job_detail', pk=pk)
    student = request.user.student_profile
    if not student.is_eligible_for_jobs():
        messages.error(request, 'Internship applications open once you reach 300 level.')
        return redirect('job_list')
    if Application.objects.filter(student=student, job=job).exists():
        messages.warning(request, 'Already applied!'); return redirect('job_detail', pk=pk)
    if request.method == 'POST':
        app = Application.objects.create(student=student, job=job, cover_letter=request.POST.get('cover_letter',''))
        StatusHistory.objects.create(application=app, status=app.status)
        messages.success(request, 'Application submitted!')
        return redirect('my_applications')
    return render(request, 'applications/apply.html', {'job':job})

@login_required
def my_applications(request):
    if not request.user.is_student(): return redirect('dashboard')
    apps = Application.objects.filter(student=request.user.student_profile).select_related('job','job__employer').prefetch_related('status_history')
    return render(request, 'applications/my_applications.html', {'applications':apps})

@login_required
def employer_applications(request):
    if not request.user.is_employer(): return redirect('dashboard')
    jobs = JobListing.objects.filter(employer=request.user.employer_profile).prefetch_related('applications__student__user')
    return render(request, 'applications/employer_applications.html', {'jobs':jobs})

@login_required
def update_status(request, pk):
    if not request.user.is_employer(): return redirect('dashboard')
    app = get_object_or_404(Application, pk=pk, job__employer=request.user.employer_profile)
    if request.method == 'POST':
        new = request.POST.get('status')
        if new in dict(Application.STATUS_CHOICES) and new != app.status:
            app.status = new; app.save()
            StatusHistory.objects.create(application=app, status=new)
            messages.success(request, f'Status updated to {app.get_status_display()}.')
    return redirect('employer_applications')

@login_required
def application_detail(request, pk):
    app = get_object_or_404(
        Application.objects.select_related('student__user', 'job__employer__user'), pk=pk
    )
    if not _can_view_application(request.user, app):
        raise PermissionDenied

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(application=app, sender=request.user, content=content)
        return redirect('application_detail', pk=pk)

    app.messages.exclude(sender=request.user).update(is_read=True)
    thread = app.messages.select_related('sender')

    cv_type = None
    cv_filename = None
    cv = app.student.cv
    if cv:
        name = cv.name.lower()
        cv_filename = os.path.basename(cv.name)
        if name.endswith('.pdf'): cv_type = 'pdf'
        elif name.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')): cv_type = 'image'
        else: cv_type = 'other'

    matched_skills, missing_skills = compute_skill_gap(app.student, app.job)

    return render(request, 'applications/application_detail.html', {
        'app': app, 'thread': thread, 'cv_type': cv_type, 'cv_filename': cv_filename,
        'matched_skills': matched_skills, 'missing_skills': missing_skills,
        'total_required_skills': len(matched_skills) + len(missing_skills),
    })

@login_required
def delete_message(request, pk):
    msg = get_object_or_404(
        Message.objects.select_related('application__student__user', 'application__job__employer__user'), pk=pk
    )
    if not _can_view_application(request.user, msg.application):
        raise PermissionDenied
    if msg.sender_id != request.user.id:
        raise PermissionDenied
    if request.method == 'POST':
        msg.is_deleted = True
        msg.save(update_fields=['is_deleted'])
    return redirect('application_detail', pk=msg.application_id)

@login_required
@xframe_options_exempt
def serve_cv_inline(request, pk):
    app = get_object_or_404(
        Application.objects.select_related('student__user', 'job__employer__user'), pk=pk
    )
    if not _can_view_application(request.user, app):
        raise PermissionDenied

    cv = app.student.cv
    if not cv:
        raise Http404('No CV uploaded.')

    filename = os.path.basename(cv.name)
    is_pdf = cv.name.lower().endswith('.pdf')
    guessed_type = mimetypes.guess_type(cv.name)[0] or 'application/octet-stream'

    if request.GET.get('download'):
        # Real downloads: honest content type, forces the save dialog.
        content_type = guessed_type
        disposition = 'attachment'
    else:
        # Inline preview: PDF.js fetches this as raw bytes and sniffs the
        # PDF signature itself, so it doesn't need (or want) a
        # download-manager-recognizable "application/pdf" content type here.
        # Images still need their real MIME type since they're rendered
        # natively via <img src="...">.
        content_type = 'application/octet-stream' if is_pdf else guessed_type
        disposition = 'inline'

    response = FileResponse(cv.open('rb'), content_type=content_type)
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return response

@login_required
def my_recommendations(request):
    if not request.user.is_student(): return redirect('dashboard')
    student = request.user.student_profile
    if not student.is_eligible_for_jobs():
        return render(request, 'jobs/ineligible.html')
    save_recommendations(student, list(JobListing.objects.filter(status='open', employer__is_verified=True)))
    recs = list(Recommendation.objects.filter(student=student).select_related('job','job__employer'))
    for rec in recs:
        rec.matched_skills, rec.missing_skills = compute_skill_gap(student, rec.job)
        rec.match_score = rec.compatibility_score  # already the blended score, stored by save_recommendations
    return render(request, 'applications/recommendations.html', {'recommendations':recs})
