from django.db import migrations, models


def backfill_company_email(apps, schema_editor):
    EmployerProfile = apps.get_model('accounts', 'EmployerProfile')
    for emp in EmployerProfile.objects.select_related('user').all():
        emp.company_email = emp.user.email
        emp.save(update_fields=['company_email'])


def noop(apps, schema_editor):
    pass  # not reversible: can't tell backfilled emails from genuinely-entered ones


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_split_html_css_skill'),
    ]

    operations = [
        migrations.AddField(
            model_name='employerprofile',
            name='company_email',
            field=models.EmailField(default='', max_length=254, help_text='Company contact email, used for verification review'),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_company_email, noop),
        migrations.AlterField(
            model_name='employerprofile',
            name='website',
            field=models.URLField(),
        ),
    ]
