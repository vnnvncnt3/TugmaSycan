import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ALLOWED_EXTENSIONS, MAX_FILE_MB, MAX_FILES, UploadBatchForm
from .models import Resume, ResumeBatch

BATCH_PAGE_SIZE = 10
RESUME_PAGE_SIZE = 20


def _querystring(request):
    """Current GET params without 'page', for pagination links."""
    params = request.GET.copy()
    params.pop('page', None)
    return params.urlencode()


def _fair_review_default(user):
    """User's saved Fair Review preference (False if they have no settings row yet)."""
    return bool(getattr(getattr(user, 'usersettings', None), 'default_fair_review', False))


def _guess_name(filename):
    # STUB: placeholder until text extraction fills in the real candidate name.
    stem = os.path.splitext(os.path.basename(filename))[0]
    return stem.replace('_', ' ').replace('-', ' ').strip().title()[:100] or 'Unnamed candidate'


@login_required
def batch_list_view(request):
    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()

    batches = (
        ResumeBatch.objects.filter(user=request.user)
        .annotate(
            resume_count=Count('resumes'),
            attention_count=Count(
                'resumes',
                filter=Q(resumes__status__in=[Resume.Status.REJECTED, Resume.Status.FAILED]),
            ),
        )
        .order_by('-upload_at')
    )
    if status in ResumeBatch.Status.values:
        batches = batches.filter(status=status)
    else:
        status = ''
    if q:
        batches = batches.filter(batch_name__icontains=q)

    page_obj = Paginator(batches, BATCH_PAGE_SIZE).get_page(request.GET.get('page'))
    return render(request, 'resumes/batch_list.html', {
        'page_obj': page_obj,
        'status_choices': ResumeBatch.Status.choices,
        'current_status': status,
        'q': q,
        'querystring': _querystring(request),
        'has_filters': bool(status or q),
    })


@login_required
def upload_view(request):
    if request.method == 'POST':
        form = UploadBatchForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['files']
            with transaction.atomic():
                # STUB: batch stays 'Processing' and resumes stay 'Uploaded' until the
                # extraction + scoring backend exists and updates their status.
                batch = ResumeBatch.objects.create(user=request.user, batch_name=form.cleaned_data['batch_name'])
                for f in files:
                    stored_path = default_storage.save(f'resumes/{request.user.pk}/{f.name}', f, max_length=255)
                    Resume.objects.create(
                        batch=batch,
                        candidate_name=_guess_name(f.name),
                        candidate_email='',
                        file_path=stored_path,
                        status=Resume.Status.UPLOADED,
                    )
            messages.success(
                request,
                f'Saved {len(files)} resume{"s" if len(files) != 1 else ""} to "{batch.batch_name}". '
                'Text extraction is not connected yet, so they stay in Uploaded status.',
            )
            return redirect('resumes:batch_detail', pk=batch.pk)
    else:
        form = UploadBatchForm(initial={'batch_name': f'Batch {timezone.localdate():%b %d, %Y}'})

    return render(request, 'resumes/upload.html', {
        'form': form,
        'allowed_extensions': ', '.join(e.lstrip('.').upper() for e in ALLOWED_EXTENSIONS),
        'accept': ','.join(ALLOWED_EXTENSIONS),
        'max_mb': MAX_FILE_MB,
        'max_files': MAX_FILES,
    })


@login_required
def batch_detail_view(request, pk):
    batch = get_object_or_404(ResumeBatch, pk=pk, user=request.user)
    status = request.GET.get('status', '')
    q = request.GET.get('q', '').strip()

    resumes = batch.resumes.annotate(skill_count=Count('resume_skills')).order_by('candidate_name', 'pk')
    if status in Resume.Status.values:
        resumes = resumes.filter(status=status)
    else:
        status = ''
    if q:
        resumes = resumes.filter(Q(candidate_name__icontains=q) | Q(candidate_email__icontains=q))

    page_obj = Paginator(resumes, RESUME_PAGE_SIZE).get_page(request.GET.get('page'))
    page_obj.object_list = list(page_obj.object_list)
    for resume in page_obj.object_list:
        resume.file_name = os.path.basename(resume.file_path)

    stats = batch.resumes.aggregate(
        total=Count('pk'),
        parsed=Count('pk', filter=Q(status__in=[Resume.Status.PARSED, Resume.Status.SCORED])),
        attention=Count('pk', filter=Q(status__in=[Resume.Status.REJECTED, Resume.Status.FAILED])),
    )
    return render(request, 'resumes/batch_detail.html', {
        'batch': batch,
        'stats': stats,
        'page_obj': page_obj,
        'status_choices': Resume.Status.choices,
        'current_status': status,
        'q': q,
        'querystring': _querystring(request),
        'has_filters': bool(status or q),
        'fair_default': _fair_review_default(request.user),
    })


@login_required
@require_POST
def batch_delete_view(request, pk):
    batch = get_object_or_404(ResumeBatch, pk=pk, user=request.user)
    stored_paths = list(batch.resumes.values_list('file_path', flat=True))
    name = batch.batch_name
    batch.delete()  # resumes, parsed entries and scores cascade
    for path in stored_paths:
        default_storage.delete(path)
    messages.success(request, f'Deleted batch "{name}" and its resumes.')
    return redirect('resumes:batch_list')


@login_required
def resume_detail_view(request, pk):
    resume = get_object_or_404(Resume.objects.select_related('batch'), pk=pk, batch__user=request.user)
    resume.file_name = os.path.basename(resume.file_path)
    return render(request, 'resumes/resume_detail.html', {
        'resume': resume,
        'resume_skills': resume.resume_skills.select_related('skill').order_by('skill__skill_name'),
        'experience': resume.experience_entries.order_by(F('end_date').desc(nulls_first=True), '-start_date'),
        'education': resume.education_entries.order_by(F('end_date').desc(nulls_first=True), '-start_date'),
        'certifications': resume.certifications.order_by('-date_obtained'),
        'fair_default': _fair_review_default(request.user),
    })
