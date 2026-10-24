from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.job_requirements.models import JobRequirement
from apps.resumes.models import ResumeBatch
from apps.scoring.models import MatchBreakdown
from apps.scoring.ranking import build_ranking
from apps.scoring.services import score_batches
from apps.user_settings.utils import fair_review_default

from .forms import RunScreeningForm
from .models import SearchHistory

HISTORY_PAGE_SIZE = 10
RESULTS_PAGE_SIZE = 20


def _querystring(request):
    params = request.GET.copy()
    params.pop('page', None)
    return params.urlencode()


@login_required
def history_view(request):
    requirement_id = request.GET.get('requirement', '')
    searches = (
        SearchHistory.objects.filter(user=request.user)
        .select_related('job_requirement')
        .annotate(scored_count=Count('candidate_scores'))
        .order_by('-searched_at')
    )
    if requirement_id.isdigit():
        searches = searches.filter(job_requirement_id=int(requirement_id))
    else:
        requirement_id = ''

    page_obj = Paginator(searches, HISTORY_PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'search_history/history_list.html', {
        'page_obj': page_obj,
        'requirements': JobRequirement.objects.filter(user=request.user).order_by('title'),
        'current_requirement': requirement_id,
        'querystring': _querystring(request),
        'has_filters': bool(requirement_id),
    })


@login_required
def run_view(request):
    if request.method == 'POST':
        form = RunScreeningForm(request.user, request.POST)
        if form.is_valid():
            search = SearchHistory.objects.create(user=request.user, job_requirement=form.cleaned_data['requirement'])
            score_batches(search, form.cleaned_data['batches'])  # STUB: see apps/scoring/services.py
            messages.success(
                request,
                'Screening saved to your history. Scoring is not connected yet, so no candidates were scored.',
            )
            return redirect('search_history:detail', pk=search.pk)
        selected = set(request.POST.getlist('batches'))
    else:
        initial = {}
        requirement_id = request.GET.get('requirement', '')
        if requirement_id.isdigit():
            initial['requirement'] = int(requirement_id)
        form = RunScreeningForm(request.user, initial=initial)
        selected = {request.GET.get('batch', '')}

    batches = list(
        ResumeBatch.objects.filter(user=request.user)
        .annotate(resume_count=Count('resumes'))
        .order_by('-upload_at')
    )
    return render(request, 'search_history/run.html', {
        'form': form,
        'batches': batches,
        'selected': selected,
        'has_requirements': form.fields['requirement'].queryset.exists(),
    })


@login_required
def detail_view(request, pk):
    search = get_object_or_404(SearchHistory.objects.select_related('job_requirement'), pk=pk, user=request.user)
    q = request.GET.get('q', '').strip()

    all_scores = search.candidate_scores.all()
    stats = all_scores.aggregate(total=Count('pk'), top=Max('total_score'), average=Avg('total_score'))
    _, rank_by_id = build_ranking(all_scores)

    scores = all_scores.select_related('resume__batch').order_by('-total_score', 'resume__candidate_name', 'pk')
    if q:
        scores = scores.filter(Q(resume__candidate_name__icontains=q) | Q(resume__candidate_email__icontains=q))

    page_obj = Paginator(scores, RESULTS_PAGE_SIZE).get_page(request.GET.get('page'))
    page_obj.object_list = list(page_obj.object_list)

    # Met / Partial / Missing counts for the rows on this page, in one query.
    counts = {}
    rows = (
        MatchBreakdown.objects.filter(candidate_score__in=[s.pk for s in page_obj.object_list])
        .values('candidate_score', 'status').annotate(n=Count('pk'))
    )
    for row in rows:
        counts.setdefault(row['candidate_score'], {})[row['status']] = row['n']
    for s in page_obj.object_list:
        by_status = counts.get(s.pk, {})
        s.rank = rank_by_id[s.pk]
        s.met = by_status.get(MatchBreakdown.Status.MET, 0)
        s.partial = by_status.get(MatchBreakdown.Status.PARTIAL, 0)
        s.missing = by_status.get(MatchBreakdown.Status.MISSING, 0)

    return render(request, 'search_history/results.html', {
        'search': search,
        'requirement': search.job_requirement,
        'criteria_count': search.job_requirement.criteria.count(),
        'stats': stats,
        'page_obj': page_obj,
        'q': q,
        'querystring': _querystring(request),
        'fair_default': fair_review_default(request.user),
    })


@login_required
@require_POST
def delete_view(request, pk):
    search = get_object_or_404(SearchHistory, pk=pk, user=request.user)
    search.delete()  # its candidate scores and breakdowns are deleted with it
    messages.success(request, 'Screening deleted.')
    return redirect('search_history:history')
