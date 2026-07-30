from django.db import migrations


def backfill_status_history(apps, schema_editor):
    Application = apps.get_model('applications', 'Application')
    StatusHistory = apps.get_model('applications', 'StatusHistory')

    for app in Application.objects.all():
        if StatusHistory.objects.filter(application=app).exists():
            continue
        entry = StatusHistory.objects.create(application=app, status=app.status)
        # changed_at is auto_now_add, so it stamps "now" on create; backdate it
        # to the application's last-updated time, the best available proxy for
        # when this status was actually set.
        StatusHistory.objects.filter(pk=entry.pk).update(changed_at=app.updated_at)


def noop(apps, schema_editor):
    pass  # not reversible: we can't know which rows were backfilled vs. real


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0004_remove_application_tracking_code'),
    ]

    operations = [
        migrations.RunPython(backfill_status_history, noop),
    ]
