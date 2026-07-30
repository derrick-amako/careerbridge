from django.db import migrations


def split_combined_skill(raw, combined, parts):
    """Return (new_value, changed). Only rewrites the string if `combined`
    is actually present as one of its comma-separated tokens; otherwise the
    original string is returned untouched (no cosmetic reformatting of
    unrelated records)."""
    tokens = [t.strip() for t in raw.split(',') if t.strip()]
    if combined.lower() not in [t.lower() for t in tokens]:
        return raw, False
    fixed, seen = [], set()
    for token in tokens:
        pieces = list(parts) if token.lower() == combined.lower() else [token]
        for piece in pieces:
            key = piece.lower()
            if key in seen:
                continue
            seen.add(key)
            fixed.append(piece)
    return ', '.join(fixed), True


def split_html_css_forward(apps, schema_editor):
    StudentProfile = apps.get_model('accounts', 'StudentProfile')
    JobListing = apps.get_model('jobs', 'JobListing')

    for sp in StudentProfile.objects.all():
        new_skills, changed = split_combined_skill(sp.skills, 'HTML/CSS', ['HTML', 'CSS'])
        if changed:
            sp.skills = new_skills
            sp.save(update_fields=['skills'])

    for job in JobListing.objects.all():
        new_required, changed = split_combined_skill(job.required_skills, 'HTML/CSS', ['HTML', 'CSS'])
        if changed:
            job.required_skills = new_required
            job.save(update_fields=['required_skills'])


def split_html_css_reverse(apps, schema_editor):
    pass  # not reversible: original combined vs. already-separate values can't be told apart


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_profile_picture'),
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(split_html_css_forward, split_html_css_reverse),
    ]
