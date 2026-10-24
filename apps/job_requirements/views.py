from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.skills.models import Skill

from .forms import RequirementForm, build_criteria_formset
from .models import JobRequirement

PAGE_SIZE = 10


def _querystring(request):
    params = request.GET.copy()
    params.pop('page', None)
    return params.urlencode()


@login_required
def requirement_list_view(request):
    q = request.GET.get('q', '').strip()
    requirements = (
        JobRequirement.objects.filter(user=request.user)
        .annotate(
            criteria_count=Count('criteria', distinct=True),
            screening_count=Count('search_history', distinct=True),
        )
        .order_by('-created_at')
    )
    if q:
        requirements = requirements.filter(title__icontains=q)

    page_obj = Paginator(requirements, PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'job_requirements/requirement_list.html', {
        'page_obj': page_obj,
        'q': q,
        'querystring': _querystring(request),
    })


def _requirement_form(request, requirement):
    """Shared by 'new' and 'edit': one page with the title and a list of criteria rows."""
    is_edit = requirement is not None
    instance = requirement if is_edit else JobRequirement(user=request.user)
    Formset = build_criteria_formset(extra=0 if is_edit else 2)

    if request.method == 'POST':
        form = RequirementForm(request.POST, instance=instance)
        formset = Formset(request.POST, instance=instance)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    saved = form.save()
                    formset.save()
            except ProtectedError:
                # MatchBreakdown rows from past screenings still point at a removed criterion.
                messages.error(
                    request,
                    "Some criteria you removed are used by past screening results, so they can't be deleted.",
                )
            else:
                messages.success(request, f'Saved "{saved.title}".')
                return redirect('job_requirements:detail', pk=saved.pk)
    else:
        form = RequirementForm(instance=instance)
        formset = Formset(instance=instance)

    return render(request, 'job_requirements/requirement_form.html', {
        'form': form,
        'formset': formset,
        'requirement': requirement,
        'is_edit': is_edit,
        'screening_count': requirement.search_history.count() if is_edit else 0,
        'skill_options': list(Skill.objects.order_by('skill_name').values_list('skill_name', flat=True)),
    })


@login_required
def new_requirement_view(request):
    return _requirement_form(request, None)


@login_required
def edit_requirement_view(request, pk):
    requirement = get_object_or_404(JobRequirement, pk=pk, user=request.user)
    return _requirement_form(request, requirement)


@login_required
def requirement_detail_view(request, pk):
    requirement = get_object_or_404(JobRequirement, pk=pk, user=request.user)
    return render(request, 'job_requirements/requirement_detail.html', {
        'requirement': requirement,
        'criteria': requirement.criteria.select_related('skill').order_by('criterion_type', 'skill__skill_name'),
        'screenings': (
            requirement.search_history
            .annotate(scored_count=Count('candidate_scores'))
            .order_by('-searched_at')[:10]
        ),
        'screening_count': requirement.search_history.count(),
    })


@login_required
@require_POST
def requirement_delete_view(request, pk):
    requirement = get_object_or_404(JobRequirement, pk=pk, user=request.user)
    if requirement.search_history.exists():
        messages.error(request, 'This requirement is used by past screenings, so it cannot be deleted.')
        return redirect('job_requirements:detail', pk=pk)
    title = requirement.title
    try:
        requirement.delete()  # its criteria are deleted with it
    except ProtectedError:
        messages.error(request, 'This requirement is still referenced by saved results, so it cannot be deleted.')
        return redirect('job_requirements:detail', pk=pk)
    messages.success(request, f'Deleted "{title}".')
    return redirect('job_requirements:list')
