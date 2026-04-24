from django.db import models
from .models import Candidate, Job
from django.contrib.auth.models import User

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"{self.candidate.user.username} applied to {self.job.title}"
