from django.contrib.auth.models import AbstractUser
from django.db import models

# Single source of truth for skill suggestions, shared by the student
# skills field and the employer job-posting required-skills field, so both
# sides of the matching engine draw from the exact same vocabulary.
SKILL_OPTIONS = [
    'Python', 'Java', 'JavaScript', 'C++', 'C#',
    'SQL', 'Django', 'React', 'Node.js', 'HTML', 'CSS',
    'Data Analysis', 'Machine Learning', 'Excel', 'Git',
    'Project Management', 'Public Speaking', 'Communication',
    'Teamwork', 'Problem Solving', 'Leadership', 'Graphic Design',
    'Microsoft Office', 'Networking', 'Cloud Computing (AWS/Azure)',
    'Digital Marketing', 'Content Writing', 'Customer Service',
    'Accounting', 'Research', 'Time Management',
]

class CustomUser(AbstractUser):
    ROLE_CHOICES = [('student','Student'),('employer','Employer'),('admin','Career Services Admin')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    def is_student(self): return self.role == 'student'
    def is_employer(self): return self.role == 'employer'
    def is_career_admin(self): return self.role == 'admin'

class StudentProfile(models.Model):
    LEVEL_CHOICES = [(str(i), f'{i}00 Level') for i in range(3,7)]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student_profile')
    department = models.CharField(max_length=200)
    level = models.CharField(max_length=5, choices=LEVEL_CHOICES, default='3')
    skills = models.TextField(help_text="Comma-separated skills")
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    cv = models.FileField(upload_to='cvs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def skills_list(self): return [s.strip() for s in self.skills.split(',') if s.strip()]
    def is_eligible_for_jobs(self):
        try: return int(self.level) >= 3
        except (TypeError, ValueError): return False
    def __str__(self): return f"{self.user.get_full_name()} - Student"

class EmployerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=200)
    company_email = models.EmailField(help_text="Company contact email, used for verification review")
    industry = models.CharField(max_length=100)
    company_description = models.TextField(blank=True)
    website = models.URLField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False, help_text="Explicitly denied by Career Services (distinct from just pending)")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.company_name
