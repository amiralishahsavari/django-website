
#admin.site.register(Jobseeker)
#admin.site.register(Employer)
#admin.site.register(project)
#admin.site.register(Application)
# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Jobseeker, Employer, project, Application

# ثبت مدل User با تنظیمات پیش‌فرض
#admin.site.register(User, UserAdmin)

@admin.register(Jobseeker)
class JobseekerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'gpa')
    search_fields = ('user__username', 'full_name', 'phone_number')
    list_filter = ('gpa',)

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('user',"full_name", 'company_name', 'phone_number')
    search_fields = ('user__username', 'company_name')
    list_filter = ('company_name',)

@admin.register(project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'required_candidates', 'salary', 'created_at')
    search_fields = ('title', 'employer__company_name')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job_seeker', 'project', 'status')
    list_filter = ('status',)