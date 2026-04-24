#use ai feature for candidate to job suggestion

import openai
from .models import Candidate, Job
def suggest_jobs_for_candidate(candidate_id):
    candidate = Candidate.objects.get(id=candidate_id)
    jobs = Job.objects.filter(status='Open')
    job_descriptions = [job.description for job in jobs]
    prompt = f"Suggest suitable jobs for a candidate with the following profile:\n\nBio: {candidate.bio}\n\nResume: {candidate.resume.url if candidate.resume else 'No resume uploaded'}\n\nAvailable jobs:\n" + "\n".join(job_descriptions)
    
    openai.api_key = 'sk-proj-DwyR8N3hszVibOr5JyqWVCLcKx-cjRSkO9wwWBnSZx-GqR6Md0LRU2Yv1eugqbcP7WzakDJ_i5T3BlbkFJh9vop8Ly-n8Yd-GckhdgUl6pLcwm3hvRUjtb5BLInpYhkTYoduYgogdF5IAYobVIONRENiCCgAy'
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    
    suggested_jobs = response.choices[0].text.strip()
    return suggested_jobs