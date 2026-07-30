from django.db import models
from accounts.models import EmployerProfile

class JobListing(models.Model):
    JOB_TYPE = [('internship','Internship'),('part_time','Part-Time'),('full_time','Full-Time'),('remote','Remote')]
    STATUS = [('open','Open'),('closed','Closed')]
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='job_listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE, default='internship')
    deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    def skills_list(self): return [s.strip() for s in self.required_skills.split(',') if s.strip()]
    def __str__(self): return f"{self.title} @ {self.employer.company_name}"
    class Meta: ordering = ['-created_at']
