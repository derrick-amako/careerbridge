from django.core.mail.backends.base import BaseEmailBackend


class PlainConsoleEmailBackend(BaseEmailBackend):
    """Dev-only email backend: prints each message as plain text, with no
    MIME/RFC-822 encoding pipeline involved. Django's built-in console
    backend runs messages through the same quoted-printable encoding used
    for real delivery, which inserts "=" soft-line-break artifacts into any
    line over 76-998 chars (URLs included), harmless for a real mail
    client that decodes it, but it corrupts the text if a human copies it
    straight out of the terminal. Since nothing here is actually being
    delivered, there's no reason to encode it at all."""

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        for message in email_messages:
            print('-' * 79)
            print('To:', ', '.join(message.to))
            print('From:', message.from_email)
            print('Subject:', message.subject)
            print()
            print(message.body)
            print('-' * 79)
        return len(email_messages)
