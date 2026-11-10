import re
from pathlib import Path

from django.core.files.storage import default_storage
from docx import Document
from pypdf import PdfReader

from .models import Resume, ResumeSkill

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
MIN_TEXT_CHARS = 30   # fewer than this usually means a scanned PDF with no text layer


def extract_text(stored_path):
    ext = Path(stored_path).suffix.lower()
    with default_storage.open(stored_path, "rb") as f:
        if ext == ".pdf":
            return "\n".join((page.extract_text() or "") for page in PdfReader(f).pages)
        if ext == ".docx":
            return "\n".join(p.text for p in Document(f).paragraphs)
    return ""


def find_skills(text, skills):
    found = []
    for skill in skills:
        pattern = r"(?<![\w+#])" + re.escape(skill.skill_name) + r"(?![\w+#])"
        if re.search(pattern, text, re.IGNORECASE):
            found.append(skill)
    return found


def parse_resume(resume, skills):
    try:
        text = extract_text(resume.file_path)
    except Exception:
        resume.status = Resume.Status.FAILED
        resume.save(update_fields=["status"])
        return
    if len(text.strip()) < MIN_TEXT_CHARS:
        resume.status = Resume.Status.REJECTED
        resume.save(update_fields=["status"])
        return
    match = EMAIL_RE.search(text)
    resume.raw_text = text
    resume.candidate_email = match.group(0)[:100] if match else ""
    resume.status = Resume.Status.PARSED
    resume.save(update_fields=["raw_text", "candidate_email", "status"])
    ResumeSkill.objects.bulk_create(ResumeSkill(resume=resume, skill=s) for s in find_skills(text, skills))