from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from apps.user_settings.utils import fair_review_default

from .models import CandidateScore, MatchBreakdown
from .ranking import build_ranking


@login_required
def candidate_detail_view(request, pk):
    score = get_object_or_404(
        CandidateScore.objects.select_related('resume__batch', 'job_requirement', 'search_history'),
        pk=pk,
        search_history__user=request.user,
    )
    items = list(
        score.breakdown_items.select_related('criterion__skill')
        .order_by('criterion__criterion_type', 'criterion__skill__skill_name')
    )
    counts = {
        'met': sum(1 for i in items if i.status == MatchBreakdown.Status.MET),
        'partial': sum(1 for i in items if i.status == MatchBreakdown.Status.PARTIAL),
        'missing': sum(1 for i in items if i.status == MatchBreakdown.Status.MISSING),
    }

    ordered_ids, rank_by_id = build_ranking(score.search_history.candidate_scores.all())
    position = ordered_ids.index(score.pk)
    return render(request, 'scoring/candidate_detail.html', {
        'score': score,
        'items': items,
        'counts': counts,
        'rank': rank_by_id[score.pk],
        'total_candidates': len(ordered_ids),
        'previous_id': ordered_ids[position - 1] if position > 0 else None,
        'next_id': ordered_ids[position + 1] if position + 1 < len(ordered_ids) else None,
        'fair_default': fair_review_default(request.user),
    })
