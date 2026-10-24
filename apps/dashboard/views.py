from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.resumes.models import ResumeBatch
from apps.job_requirements.models import JobRequirement
from apps.scoring.models import CandidateScore


@login_required
def dashboard_view(request):
    recent_batches = ResumeBatch.objects.filter(user=request.user).order_by('-upload_at')[:5]
    recent_requirements = JobRequirement.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'recent_batches': recent_batches,
        'recent_requirements': recent_requirements,
        'total_batches': ResumeBatch.objects.filter(user=request.user).count(),
        'total_requirements': JobRequirement.objects.filter(user=request.user).count(),
        'total_scored': CandidateScore.objects.filter(resume__batch__user=request.user).count(),
    }
    return render(request, 'dashboard/dashboard.html', context)