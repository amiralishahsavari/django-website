from winreg import DeleteKey
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login  
from .forms import *
from django.db.models import Q
#optional 
from .decorators import jobseeker_required, employer_required


# views.py

# controlling the system 
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('login')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    context = {}
    try:
        if hasattr(request.user, 'jobseeker'):
            context['user_type'] = 'jobseeker'
            context['profile'] = request.user.jobseeker
        elif hasattr(request.user, 'employer'):
            context['user_type'] = 'employer'
            context['profile'] = request.user.employer
    except Exception as e:
        pass  # یا مدیریت خطا مناسب
    
    return render(request, 'home.html', context)

@login_required
def update_email(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        request.user.email = email
        request.user.save()
    return redirect('home')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user_type = request.POST.get('user_type', 'jobseeker')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # بررسی تطابق رمز عبور
        if password1 != password2:
            messages.error(request, 'رمز عبور و تکرار آن مطابقت ندارند.')
            return render(request, 'registration/register.html', {
                'form': None,
                'user_type': user_type
            })

        # انتخاب فرم و مدل بر اساس نوع کاربر
        if user_type == 'jobseeker':
            form = JobSeekerRegisterForm(request.POST)
            profile_model = Jobseeker
        else:
            form = EmployerRegisterForm(request.POST)
            profile_model = Employer

        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            # Check if phone number already exists
            if Jobseeker.objects.filter(phone_number=phone_number).exists():
                messages.error(request, 'این شماره موبایل قبلاً ثبت شده است')
                return render(request, 'register.html', {
                    'form': form,
                    'user_type': user_type
                })

            user = form.save()
            profile_data = {
                'user': user,
                'phone_number': form.cleaned_data['phone_number'],
                'full_name': form.cleaned_data['full_name']
            }

            if user_type == 'jobseeker':
                profile_data['gpa'] = form.cleaned_data.get('gpa', 0.00)
            else:
                profile_data['company_name'] = form.cleaned_data['company_name']

            profile_model.objects.create(**profile_data)
            messages.success(request, 'ثبت‌ نام با موفقیت انجام شد!')
            return redirect('login')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = None

    return render(request, 'registration/register.html', {
        'form': form,
        'user_type': request.POST.get('user_type', 'jobseeker')
    })


def get_form_fields(request):
    user_type = request.GET.get('user_type', 'jobseeker')
    return render(request, f'registration/{user_type}_fields.html')

def login(request):
    if request.user.is_authenticated:
        return redirect('home')  #  اگر لاگین کرده، نره به صفحه لاگین
    
    if request.method == 'POST':
        # کدهای مربوط به ورود
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            #login(request, user)
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "نام کاربری یا رمز عبور نادرست است")
    
    return render(request, 'registration/login.html')

@login_required
def edit_profile(request):
    user = request.user
    is_jobseeker = hasattr(user, 'jobseeker')
    is_employer = hasattr(user, 'employer')

    # انتخاب فرم مناسب بر اساس نوع کاربر
    if is_jobseeker:
        profile = user.jobseeker
        profile_form_class = JobseekerProfileForm
    elif is_employer:
        profile = user.employer
        profile_form_class = EmployerProfileForm
    else:
        messages.error(request, "نوع کاربری شما مشخص نیست.")
        return redirect('home')

    if request.method == 'POST':
        profile_form = profile_form_class(request.POST, instance=profile)
        password_form = CustomPasswordChangeForm(user, request.POST)

        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, "به روزرسانی با موفقیت انجام شد.")
            return redirect('home')
        else:
            messages.error(request, "لطفاً خطاهای زیر را برطرف کنید.")
    else:
        profile_form = profile_form_class(instance=profile)
        password_form = CustomPasswordChangeForm(user, request.POST)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'is_jobseeker': is_jobseeker,
        'is_employer': is_employer
    }
    return render(request, 'registration/edit_profile.html', context)

#@login_required
#@jobseeker_required
#def send_request_view(request):
#    return HttpResponse("reloading")


#@login_required
#@jobseeker_required
#def analyze_sent_requests_view(request):
#    return HttpResponse("reloading2")

@login_required
@employer_required
def project_list(request):
    employer = request.user.employer 
    projects = project.objects.filter(employer=employer).prefetch_related('applications')
    #project.objects.filter(employer=employer).prefetch_related('requests')
    return render(request, 'employer/project_list.html', {'projects': projects})


@login_required
@employer_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.employer = request.user.employer  # اتصال به کارفرمای لاگین‌شده
            project.save()
            return redirect('home')
        else:
            messages.error(request, "خطا در ثبت پروژه. لطفاً فرم را بررسی کنید.")
    else:
        form = ProjectCreateForm()

    return render(request, 'employer/create_project.html', {'form': form})

@login_required
@jobseeker_required
def project_list_view(request):
    jobseeker = get_object_or_404(Jobseeker, user=request.user)
    applied_projects = Application.objects.filter(job_seeker=jobseeker).values_list('project_id', flat=True)
    
    Project = project.objects.all()
    
    title = request.GET.get('title')
    min_salary = request.GET.get('min_salary')
    max_salary = request.GET.get('max_salary')
    employer = request.GET.get('employer')
    only_available = request.GET.get('only_available')
    only_not_applied = request.GET.get('only_not_applied')

    filters = Q()
    if title:
        filters &= Q(title__icontains=title)
    if min_salary:
        filters &= Q(salary__gte=min_salary)
    if max_salary:
        filters &= Q(salary__lte=max_salary)
    if employer:
        filters &= Q(employer__company_name__icontains=employer)

    Project = Project.filter(filters)

    if only_available:
        Project = [p for p in Project if p.applications.count() < p.required_candidates]
    if only_not_applied:
        Project = [p for p in Project if p.id not in applied_projects]

    return render(request, 'jobseeker/project_list.html', {
        'projects': Project,
        'applied_projects': applied_projects,
    })

@login_required
@jobseeker_required
def apply_to_project(request, project_id):
    Project = get_object_or_404(project, pk=project_id)  # ← project مدل، Project متغیره
    jobseeker = get_object_or_404(Jobseeker, user=request.user)

    if Application.objects.filter(job_seeker=jobseeker, project=Project).exists():
        messages.warning(request, "شما قبلاً برای این پروژه درخواست داده‌اید.")
    elif Project.applications.count() >= Project.required_candidates:
        messages.error(request, "ظرفیت این پروژه تکمیل شده است.")
    else:
        Application.objects.create(job_seeker=jobseeker, project=Project)
        messages.success(request, "درخواست شما با موفقیت ثبت شد.")

    return redirect('job_project-list')

@login_required
@jobseeker_required
def withdraw_application(request, project_id):
    jobseeker = get_object_or_404(Jobseeker, user=request.user)
    Project = get_object_or_404(project, pk=project_id)

    try:
        application = Application.objects.get(job_seeker=jobseeker, project=Project)
        application.delete()
        messages.success(request, "درخواست شما با موفقیت حذف شد.")
    except Application.DoesNotExist:
        messages.warning(request, "درخواستی برای این پروژه ثبت نکرده‌اید.")

    return redirect(request.META.get('HTTP_REFERER', 'jobseeker-applications'))

@login_required
@jobseeker_required
def jobseeker_applications(request):
    jobseeker = get_object_or_404(Jobseeker, user=request.user)
    applications = Application.objects.filter(job_seeker=jobseeker).select_related('project__employer')

    return render(request, 'jobseeker/jobseeker_applications.html', {
        'applications': applications
    })

@login_required
def edit_project(request, project_id):
    # دریافت پروژه
    proj = get_object_or_404(project, id=project_id)

    # فقط کارفرمایی که پروژه را ایجاد کرده اجازه ویرایش دارد
    if proj.employer.user != request.user:
        messages.error(request, "شما اجازه ویرایش این پروژه را ندارید.")
        return redirect('project_list')  # یا هر صفحه مناسب دیگر

    if request.method == 'POST':
        form = EditProjectForm(request.POST, instance=proj)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = EditProjectForm(instance=proj)

    return render(request, 'employer/edit_project.html', {
        'form': form,
        'project': proj
    })

@login_required
@employer_required
def delete_project(request, project_id):
    proj = get_object_or_404(project, id=project_id)

    if proj.employer.user != request.user:
        messages.error(request, "شما اجازه حذف این پروژه را ندارید.")
        return redirect('project_list')

    if request.method == 'POST':
        proj.delete()
        return redirect('project_list')

    return render(request, 'employer/confirm_delete_project.html', {'project': proj})

@login_required
@employer_required
def review_applicants_view(request, project_id):
    proj = get_object_or_404(project, id=project_id, employer=request.user.employer)
    
    query = request.GET.get('skill', '').strip()
    
    applications = Application.objects.filter(project=proj).select_related('job_seeker')

    if query:
        applications = applications.filter(job_seeker__skill__icontains=query)

    applications = applications.order_by('-job_seeker__gpa')  # مرتب‌سازی بر اساس معدل

    return render(request, 'employer/review_applicants.html', {
        'project': proj,
        'applications': applications,
        'query': query
    })

    
@login_required
@employer_required
def change_application_status(request, app_id, status):
    application = get_object_or_404(Application, id=app_id)

    if request.user != application.project.employer.user:
        messages.error(request, "شما مجاز به تغییر این درخواست نیستید.")
        return redirect('home')

    if status in ['approved', 'rejected']:
        application.status = status
        application.save()

    return redirect('review_applicants', project_id=application.project.id)
