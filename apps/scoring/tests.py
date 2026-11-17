from decimal import Decimal

from django.test import TestCase

from apps.job_requirements.models import JobRequirement, RequirementCriterion
from apps.resumes.models import Resume, ResumeBatch, ResumeSkill
from apps.search_history.models import SearchHistory
from apps.skills.models import Skill
from apps.users.models import User

from .models import CandidateScore
from .ranking import build_ranking
from .services import score_batches

CriterionType = RequirementCriterion.CriterionType


class ScoreBatchesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='tester@example.com')
        self.python = Skill.objects.create(skill_name='Python')
        self.django_skill = Skill.objects.create(skill_name='Django')
        self.requirement = JobRequirement.objects.create(user=self.user, title='Junior Backend Developer')
        RequirementCriterion.objects.create(
            job_requirement=self.requirement, skill=self.python, criterion_type=CriterionType.SKILL)
        RequirementCriterion.objects.create(
            job_requirement=self.requirement, skill=self.django_skill,
            criterion_type=CriterionType.EXPERIENCE, min_years=2)
        self.batch = ResumeBatch.objects.create(user=self.user, batch_name='Test batch')
        self.search = SearchHistory.objects.create(user=self.user, job_requirement=self.requirement)

    def make_resume(self, name, raw_text='', skills=()):
        resume = Resume.objects.create(
            batch=self.batch, candidate_name=name, candidate_email='',
            file_path=f'resumes/test/{name}.docx', raw_text=raw_text, status=Resume.Status.PARSED)
        ResumeSkill.objects.bulk_create(ResumeSkill(resume=resume, skill=s) for s in skills)
        return resume

    def test_met_and_partial_total(self):
        self.make_resume('ana', skills=[self.python, self.django_skill])
        self.assertEqual(score_batches(self.search, [self.batch]), 1)
        self.assertEqual(CandidateScore.objects.get().total_score, Decimal('75.00'))

    def test_missing_scores_zero(self):
        self.make_resume('dino')
        score_batches(self.search, [self.batch])
        self.assertEqual(CandidateScore.objects.get().total_score, Decimal('0.00'))

    def test_skill_added_after_upload_still_matches(self):
        self.make_resume('ben', raw_text='Knows Python and Django well.')
        score_batches(self.search, [self.batch])
        self.assertEqual(CandidateScore.objects.get().total_score, Decimal('75.00'))

    def test_no_criteria_returns_zero(self):
        empty = JobRequirement.objects.create(user=self.user, title='Empty')
        search = SearchHistory.objects.create(user=self.user, job_requirement=empty)
        self.make_resume('carla', skills=[self.python])
        self.assertEqual(score_batches(search, [self.batch]), 0)

    def test_tied_scores_share_a_rank(self):
        self.make_resume('ana', skills=[self.python, self.django_skill])
        self.make_resume('ben', skills=[self.python])
        self.make_resume('carla', skills=[self.python])
        score_batches(self.search, [self.batch])
        _, rank_by_id = build_ranking(self.search.candidate_scores.all())
        self.assertEqual(sorted(rank_by_id.values()), [1, 2, 2])
