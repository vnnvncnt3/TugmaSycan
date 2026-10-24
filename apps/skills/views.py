from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import Lower
from django.shortcuts import redirect, render

from .forms import SkillForm
from .models import Skill

PAGE_SIZE = 30


def _querystring(request):
    params = request.GET.copy()
    params.pop('page', None)
    return params.urlencode()


@login_required
def skill_list_view(request):
    # Skills are shared by every user; any signed-in user may add one.
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save()
            messages.success(request, f'Added "{skill.skill_name}" to the library.')
            return redirect('skills:list')
    else:
        form = SkillForm()

    q = request.GET.get('q', '').strip()
    scope = request.GET.get('scope', '')

    # Usage counts are limited to the current user's own resumes and requirements.
    skills = Skill.objects.annotate(
        resume_count=Count(
            'resume_skills',
            filter=Q(resume_skills__resume__batch__user=request.user),
            distinct=True,
        ),
        requirement_count=Count(
            'requirement_criteria',
            filter=Q(requirement_criteria__job_requirement__user=request.user),
            distinct=True,
        ),
    ).order_by(Lower('skill_name'))

    if q:
        skills = skills.filter(skill_name__icontains=q)
    if scope == 'resumes':
        skills = skills.filter(resume_count__gt=0)
    elif scope == 'requirements':
        skills = skills.filter(requirement_count__gt=0)
    else:
        scope = ''

    page_obj = Paginator(skills, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'skills/skill_list.html', {
        'form': form,
        'page_obj': page_obj,
        'q': q,
        'scope': scope,
        'querystring': _querystring(request),
        'has_filters': bool(q or scope),
        'total_skills': Skill.objects.count(),
    })
