import os
from os.path import join, dirname

import resend
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

__all__ = ['send_password_reset_email']


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    resend.api_key = os.getenv('RESEND_API_KEY')
    resend.Emails.send(
        {
            'from': os.getenv('RESEND_FROM_EMAIL'),
            'to': [to_email],
            'subject': 'Reset your MCQ4U password',
            'html': (
                '<p>We received a request to reset your MCQ4U password.</p>'
                f'<p><a href="{reset_link}">Click here to reset your password</a>. '
                'This link expires in 1 hour.</p>'
                '<p>If you did not request this, you can safely ignore this email.</p>'
            ),
        }
    )
