from django.contrib.auth.models import User
from django.db import models

# Employer model for company info
class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employer")
    company_name = models.CharField(max_length=200)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    company_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

class Profile(models.Model):
	USER_TYPES = (
		('employer', 'Employer'),
		('candidate', 'Candidate'),
	)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	user_type = models.CharField(max_length=10, choices=USER_TYPES)

	def __str__(self):
		return f"{self.user.username} - {self.user_type}"

# Education model for candidate's education details
from django.db import models
from django.contrib.auth.models import User

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="candidate")
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True)
    experience = models.TextField(blank=True)
    cover_letter = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Education(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    year = models.CharField(max_length=10)


class Job(models.Model):
    title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    employer = models.ForeignKey('Employer', on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# JobApplication model for candidate job applications
class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    # Interview scheduling fields
    interview_date = models.DateField(blank=True, null=True)
    interview_time = models.TimeField(blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Pending')

    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"{self.candidate.user.username} applied to {self.job.title}"
