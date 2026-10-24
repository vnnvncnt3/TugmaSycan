from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def new_requirement_view(request):
    return render(request, 'job_requirements/new_coming_soon.html')