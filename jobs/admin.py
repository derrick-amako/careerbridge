from django.contrib import admin
from .models import JobListing
@admin.register(JobListing)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title','employer','job_type','status','deadline']
    list_filter = ['job_type','status']
