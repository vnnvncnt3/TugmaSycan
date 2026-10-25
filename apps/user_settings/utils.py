def fair_review_default(user):
    """The user's saved Fair Review preference (False if they have no settings row yet)."""
    return bool(getattr(getattr(user, 'usersettings', None), 'default_fair_review', False))
