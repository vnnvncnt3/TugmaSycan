def build_ranking(scores):
    """Rank a screening's CandidateScore queryset, highest total_score first.

    Returns (ordered_ids, rank_by_id). Ties share a rank (1, 2, 2, 4), so a rank
    stays the same however the list is filtered or paged.
    """
    ordered_ids = []
    rank_by_id = {}
    previous_score = None
    rank = 0
    for position, (pk, score) in enumerate(scores.order_by('-total_score', 'pk').values_list('pk', 'total_score'), start=1):
        if score != previous_score:
            rank = position
            previous_score = score
        ordered_ids.append(pk)
        rank_by_id[pk] = rank
    return ordered_ids, rank_by_id
