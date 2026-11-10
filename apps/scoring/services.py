from decimal import Decimal
from django.db import transaction
from apps.job_requirements.models import RequirementCriterion
from apps.resumes.models import Resume
from .models import CandidateScore, MatchBreakdown

Status = MatchBreakdown.Status
POINTS = {
    Status.MET: Decimal("1"),
    Status.PARTIAL: Decimal("0.5"),
    Status.MISSING: Decimal("0")
}

def score_batches(search_history, batches):
    """Rule-based: Met = skill found in the resume. An Experience criterion with minimum years is only Partial, because years are not verified. total = (met + 0.5 * partial) / criteria * 100."""
    criteria = list(search_history.job_requirement.criteria.all())
    if not criteria:
        return 0

    resumes = Resume.objects.filter(
        batch__in=batches, 
        status__in=[Resume.Status.PARSED, Resume.Status.SCORED]
    ).prefetch_related("resume_skills")

    scored = 0
    with transaction.atomic():
        for resume in resumes:
            have = {rs.skill_id for rs in resume.resume_skills.all()}
            rows, points = [], Decimal("0")
            
            for c in criteria:
                if c.skill_id not in have:
                    status = Status.MISSING
                elif c.criterion_type == RequirementCriterion.CriterionType.EXPERIENCE and c.min_years:
                    status = Status.PARTIAL
                else:
                    status = Status.MET
                
                points += POINTS[status]
                rows.append((c, status))
            
            total = (points / len(criteria) * 100).quantize(Decimal("0.01"))
            
            score = CandidateScore.objects.create(
                resume=resume,
                job_requirement=search_history.job_requirement,
                search_history=search_history,
                total_score=total,
            )
            
            MatchBreakdown.objects.bulk_create(
                MatchBreakdown(candidate_score=score, criterion=c, status=s) for c, s in rows
            )
            
            Resume.objects.filter(pk=resume.pk).update(status=Resume.Status.SCORED)
            scored += 1

    return scored