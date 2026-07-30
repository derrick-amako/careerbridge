from django.db import models
from accounts.models import StudentProfile, CustomUser
from jobs.models import JobListing

class Application(models.Model):
    STATUS_CHOICES = [('submitted','Submitted'),('under_review','Under Review'),
                      ('shortlisted','Shortlisted'),('rejected','Rejected'),('accepted','Accepted')]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    cover_letter = models.TextField(blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"{self.student.user.get_full_name()} → {self.job.title}"
    class Meta: unique_together = ['student','job']; ordering = ['-date_submitted']

class StatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Application.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['changed_at']

class Message(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    class Meta: ordering = ['timestamp']
    def __str__(self): return f"{self.sender.get_full_name()}: {self.content[:30]}"

class Recommendation(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='recommendations')
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name='recommendations')
    compatibility_score = models.FloatField()
    date_generated = models.DateTimeField(auto_now=True)
    class Meta: unique_together = ['student','job']; ordering = ['-compatibility_score']
