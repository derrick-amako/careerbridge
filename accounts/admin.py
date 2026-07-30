from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StudentProfile, EmployerProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username','email','role','first_name','last_name']
    list_filter = ['role']
    fieldsets = UserAdmin.fieldsets + (('Role', {'fields': ('role',)}),)

admin.site.register(StudentProfile)
admin.site.register(EmployerProfile)
