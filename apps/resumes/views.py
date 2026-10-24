from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def upload_view(request):
    return render(request, 'resumes/upload_coming_soon.html')