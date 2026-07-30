from django.core.exceptions import ValidationError

# Heuristic filter for obviously fake/placeholder email addresses, on top of
# Django's built-in EmailField syntax check. This CANNOT verify that a
# domain is real or that the sender actually owns it -- it only catches
# common example/test/placeholder domains and suspiciously short,
# generic-looking domain names. That's expected: real ownership can only be
# confirmed by actually delivering mail to the address, which is out of
# scope here.
BLOCKED_EMAIL_DOMAINS = {
    'example.com', 'example.org', 'example.net', 'example.edu',
    'test.com', 'testing.com', 'test.org', 'test.net',
    'fake.com', 'fakemail.com', 'notreal.com',
    'email.com',
    'domain.com', 'yourdomain.com', 'mydomain.com',
    'yourcompany.com', 'company.com', 'mycompany.com',
    'sample.com', 'samplemail.com', 'placeholder.com',
    'foo.com', 'bar.com', 'foobar.com',
    'dummy.com', 'dummymail.com', 'none.com', 'nomail.com', 'noemail.com',
    'asdf.com', 'qwerty.com', '123.com', 'abc.com',
    'myemail.com', 'user.com', 'someone.com', 'anyone.com',
    'website.com', 'site.com', 'yoursite.com',
}

# Minimum length of the domain's main label (the part before the first dot,
# e.g. "acme" in "acme.com") -- anything shorter reads as a placeholder
# rather than a real company/personal domain (e.g. "ent.com").
MIN_DOMAIN_LABEL_LENGTH = 4

INVALID_EMAIL_MESSAGE = 'Please enter a valid company/personal email address.'


def validate_real_email(value):
    """Reject common placeholder/test email domains and suspiciously short
    domain names. Runs in addition to (not instead of) EmailField's own
    syntax validation."""
    if not value or '@' not in value:
        return
    domain = value.rsplit('@', 1)[-1].strip().lower()
    if not domain:
        return
    if domain in BLOCKED_EMAIL_DOMAINS:
        raise ValidationError(INVALID_EMAIL_MESSAGE)
    label = domain.split('.')[0]
    if len(label) < MIN_DOMAIN_LABEL_LENGTH:
        raise ValidationError(INVALID_EMAIL_MESSAGE)
