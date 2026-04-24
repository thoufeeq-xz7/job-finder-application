from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),

    # Candidate features
    path('candidate/add-education/', views.add_education, name='add_education'),
    path('candidate/upload-resume/', views.upload_resume, name='upload_resume'),
    path('candidate/edit-profile/', views.edit_profile, name='edit_profile'),
    path('candidate/profile/', views.candidate_profile, name='candidate_profile'),
    path('candidate/browse-jobs/', views.browse_jobs, name='browse_jobs'),
    path('candidate/view-schedule/<int:job_id>/', views.candidate_view_schedule, name='candidate_view_schedule'),


    # Employer features
    path('employer/post-job/', views.post_job, name='post_job'),
    path('employer/view-applicants/', views.view_applicants, name='view_applicants'),
    path('employer/schedule-interview/<int:app_id>/', views.schedule_interview, name='schedule_interview'),
    path('employer/reject-application/<int:app_id>/', views.reject_application, name='reject_application'),
    path('employer/delete-application/<int:app_id>/', views.delete_application, name='delete_application'),
    path('employer/profile/', views.employer_profile, name='employer_profile'),
    path('employer/edit-profile/', views.edit_employer_profile, name='edit_employer_profile'),
    path('employer/job/<int:job_id>/', views.view_job, name='view_job'),
    path('employer/job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('employer/job/<int:job_id>/delete/', views.delete_job, name='delete_job'),

    # Admin features

]
