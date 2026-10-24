from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def history_view(request):
    return render(request, 'search_history/history_coming_soon.html')