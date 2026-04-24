# --- Candidate View Schedule ---
from django.shortcuts import get_object_or_404
# Delete application view
from django.views.decorators.http import require_POST


# Interview scheduling view
from django.views.decorators.http import require_POST

from django.http import HttpResponseForbidden

# Edit Job View
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Profile, Education, Candidate, Job, Employer
from .forms import EducationForm
from .models import JobApplication

def candidate_dashboard(request):
    candidate = ...  # get candidate object for request.user
    applied_jobs = JobApplication.objects.filter(candidate=candidate)
    # ...other context...
    return render(request, 'accounts/candidate/candidate_dashboard.html', {
        'applied_jobs': applied_jobs,
        # ...other context...
    })

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'candidate')
def candidate_profile(request):
    candidate, _ = Candidate.objects.get_or_create(user=request.user)
    return render(request, 'accounts/candidate/profile.html', {'candidate': candidate})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        user_type = request.POST['user_type']
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already exists'})
        user = User.objects.create_user(username=username, password=password, email=email)
        user.profile.user_type = user_type
        user.profile.save()
        login(request, user)
        if user_type == 'employer':
            Employer.objects.create(user=user, company_name=username)
            return redirect('employer_dashboard')
        else:
            return redirect('candidate_dashboard')
    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                return render(request, 'accounts/login.html', {'error': 'Account is inactive'})
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'profile'):
                if user.profile.user_type == 'employer':
                    return redirect('employer_dashboard')
                elif user.profile.user_type == 'candidate':
                    return redirect('candidate_dashboard')
                else:
                    return render(request, 'accounts/login.html', {'error': 'Invalid user type'})
            else:
                return render(request, 'accounts/login.html', {'error': 'No profile found'})
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    from django.contrib.auth.models import User
    from .models import Job
    user_logins = User.objects.all().order_by('-last_login')
    jobs_by_user = Job.objects.select_related('employer__user')
    # Attach user to each job for template
    for job in jobs_by_user:
        if job.employer and job.employer.user:
            job.user = job.employer.user
        else:
            job.user = None
    context = {
        'user_logins': user_logins,
        'jobs_by_user': jobs_by_user,
    }
    return render(request, 'accounts/admin/admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
def employer_dashboard(request):
    employer = getattr(request.user, 'employer', None)
    posted_jobs = []
    total_jobs = 0
    total_applications = 0
    if employer:
        posted_jobs = Job.objects.filter(company_name=employer.company_name).order_by('-created_at')
        total_jobs = posted_jobs.count()
        try:
            from .models import JobApplication
            total_applications = JobApplication.objects.filter(job__in=posted_jobs).count()
            for job in posted_jobs:
                job.application_count = JobApplication.objects.filter(job=job).count()
        except ImportError:
            for job in posted_jobs:
                job.application_count = 0
    context = {
        'employer': employer,
        'posted_jobs': posted_jobs,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
    }
    return render(request, 'accounts/employer/employer_dashboard.html', context)

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'candidate')
def candidate_dashboard(request):
    education_list = Education.objects.filter(candidate=request.user)
    candidate, created = Candidate.objects.get_or_create(user=request.user)
    from .models import JobApplication
    applied_jobs = JobApplication.objects.filter(candidate=candidate)
    return render(request, 'accounts/candidate/candidate_dashboard.html', {
        'education_list': education_list,
        'candidate': candidate,
        'applied_jobs': applied_jobs,
    })

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'candidate')
@require_http_methods(["GET", "POST"])
def add_education(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.candidate = request.user
            edu.save()
            return redirect('candidate_dashboard')
    else:
        form = EducationForm()
    return render(request, 'accounts/candidate/add_education.html', {'form': form})

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'candidate')
@require_http_methods(["GET", "POST"])
def upload_resume(request):
    candidate = getattr(request.user, 'candidate', None)
    if request.method == 'POST' and candidate:
        resume_file = request.FILES.get('resume')
        if resume_file:
            candidate.resume = resume_file
            candidate.save()
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('candidate_dashboard')
        else:
            messages.error(request, 'Please select a file to upload.')
    return render(request, 'accounts/candidate/upload_resume.html', {'candidate': candidate})

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'candidate')
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    candidate = getattr(request.user, 'candidate', None)
    if request.method == 'POST' and candidate:
        phone = request.POST.get('phone', '')
        bio = request.POST.get('bio', '')
        skills = request.POST.get('skills', '')
        experience = request.POST.get('experience', '')
        cover_letter = request.POST.get('cover_letter', '')
        candidate.phone = phone
        candidate.bio = bio
        candidate.skills = skills
        candidate.experience = experience
        candidate.cover_letter = cover_letter
        candidate.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('candidate_dashboard')
    return render(request, 'accounts/candidate/edit_profile.html', {'candidate': candidate})

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'candidate')
def browse_jobs(request):
    from .ai import suggest_jobs_for_candidate
    from .models import JobApplication
    candidate = getattr(request.user, 'candidate', None)
    jobs = Job.objects.filter(status='Open').order_by('-created_at')
    suggested_jobs = None
    if candidate:
        try:
            suggested_jobs = suggest_jobs_for_candidate(candidate.id)
        except Exception:
            suggested_jobs = None

    if request.method == 'POST' and candidate:
        job_id = request.POST.get('job_id')
        job = Job.objects.filter(id=job_id, status='Open').first()
        if job:
            # Prevent duplicate applications
            if not JobApplication.objects.filter(job=job, candidate=candidate).exists():
                JobApplication.objects.create(job=job, candidate=candidate)
                messages.success(request, 'You have successfully applied for this job!')
            else:
                messages.info(request, 'You have already applied for this job.')
        return redirect('browse_jobs')

    # Get jobs the candidate has already applied for
    applied_job_ids = JobApplication.objects.filter(candidate=candidate).values_list('job_id', flat=True) if candidate else []

    return render(request, 'accounts/candidate/browse_jobs.html', {
        'jobs': jobs,
        'suggested_jobs': suggested_jobs,
        'applied_job_ids': applied_job_ids,
    })

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
def post_job(request):
    employer = getattr(request.user, 'employer', None)
    if request.method == 'POST' and employer:
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        salary = request.POST.get('salary')
        requirements = request.POST.get('requirements')
        Job.objects.create(
            title=title,
            company_name=employer.company_name,
            description=description + (f"\n\nLocation: {location}" if location else "") + (f"\nSalary: {salary}" if salary else "") + (f"\nRequirements: {requirements}" if requirements else "")
        )
        messages.success(request, 'Job posted successfully!')
        return redirect('employer_dashboard')
    return render(request, 'accounts/employer/post_job.html')

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
def view_applicants(request):
    try:
        from .models import JobApplication
        jobs = Job.objects.filter(company_name=request.user.employer.company_name)
        applications = JobApplication.objects.filter(job__in=jobs).select_related('job', 'candidate')
    except ImportError:
        applications = []
    return render(request, 'accounts/employer/view_applicants.html', {'applications': applications})

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
def employer_profile(request):
    employer, _ = Employer.objects.get_or_create(user=request.user, defaults={"company_name": request.user.username})
    return render(request, 'accounts/employer/profile.html', {'employer': employer})

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
def edit_employer_profile(request):
    employer, _ = Employer.objects.get_or_create(user=request.user, defaults={"company_name": request.user.username})
    if request.method == 'POST':
        company_name = request.POST.get('company_name', employer.company_name)
        address = request.POST.get('address', employer.address)
        phone = request.POST.get('phone', employer.phone)
        company_description = request.POST.get('company_description', employer.company_description)
        employer.company_name = company_name
        employer.address = address
        employer.phone = phone
        employer.company_description = company_description
        employer.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('employer_profile')
    return render(request, 'accounts/employer/edit_profile.html', {'employer': employer})

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
def view_job(request, job_id):
    job = Job.objects.filter(id=job_id, company_name=request.user.employer.company_name).first()
    return render(request, 'accounts/employer/view_job.html', {'job': job})



@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
@require_http_methods(["GET", "POST"])
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company_name=request.user.employer.company_name)
    if request.method == 'POST':
        job.title = request.POST.get('title', job.title)
        job.description = request.POST.get('description', job.description)
        job.location = request.POST.get('location', getattr(job, 'location', ''))
        job.salary = request.POST.get('salary', getattr(job, 'salary', ''))
        job_type = request.POST.get('type', getattr(job, 'type', 'Full Time'))
        job_status = request.POST.get('status', job.status)
        # Save extra fields if they exist on the model
        if hasattr(job, 'location'):
            job.location = job.location
        if hasattr(job, 'salary'):
            job.salary = job.salary
        if hasattr(job, 'type'):
            job.type = job_type
        if hasattr(job, 'status'):
            job.status = job_status
        job.save()
        messages.success(request, 'Job updated successfully!')
        return redirect('employer_dashboard')
    return render(request, 'accounts/employer/edit_job.html', {'job': job})

# Close Job View

# Delete Job View
@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
@require_http_methods(["POST"])
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company_name=request.user.employer.company_name)
    job.delete()
    messages.success(request, 'Job deleted successfully!')
    return redirect('employer_dashboard')

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
@require_POST
def schedule_interview(request, app_id):
    from .models import JobApplication
    application = get_object_or_404(JobApplication, id=app_id)
    form = InterviewScheduleForm(request.POST, instance=application)
    if form.is_valid():
        app = form.save(commit=False)
        app.status = 'Interview Scheduled'
        app.save()
        messages.success(request, 'Interview scheduled successfully!')
    else:
        messages.error(request, 'Error scheduling interview. Please check the form.')
    return redirect('view_applicants')

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
@require_POST
def reject_application(request, app_id):
    from .models import JobApplication
    application = get_object_or_404(JobApplication, id=app_id)
    application.status = 'Rejected'
    application.save()
    messages.success(request, 'Application rejected.')
    return redirect('view_applicants')
from .forms import InterviewScheduleForm

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'employer')
@require_POST
def delete_application(request, app_id):
    from .models import JobApplication
    application = get_object_or_404(JobApplication, id=app_id)
    application.delete()
    messages.success(request, 'Application removed.')
    return redirect('view_applicants')

@login_required
@user_passes_test(lambda u: hasattr(u, 'profile') and u.profile.user_type == 'candidate')
def candidate_view_schedule(request, job_id):
    candidate = getattr(request.user, 'candidate', None)
    from .models import JobApplication
    application = get_object_or_404(JobApplication, job_id=job_id, candidate=candidate)
    employer_name = application.job.employer.company_name if application.job.employer else application.job.company_name
    return render(request, 'accounts/candidate/view_schedule.html', {
        'application': application,
        'employer_name': employer_name,
    })