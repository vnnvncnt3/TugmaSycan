import re

from .models import Skill


def normalize_skill_name(raw):
    """Trim and collapse inner whitespace: '  AWS   Cloud ' -> 'AWS Cloud'."""
    return re.sub(r'\s+', ' ', raw or '').strip()


def get_or_create_skill(raw_name):
    """Return (skill, created). Matching ignores upper/lower case, so 'python' reuses 'Python'."""
    name = normalize_skill_name(raw_name)
    existing = Skill.objects.filter(skill_name__iexact=name).first()
    if existing:
        return existing, False
    return Skill.objects.create(skill_name=name), True
