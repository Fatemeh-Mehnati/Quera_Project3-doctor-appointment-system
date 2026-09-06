from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import User


@override_settings(
    MAILERS={
        'default': {
            'BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
        },
    }
)
class OTPTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Test12345!'
        )

    def request_otp(self):
        response = self.client.post(
            reverse('accounts:request_otp'),
            {
                'email': 'test@example.com'
            }
        )

        self.assertEqual(response.status_code, 302)

        return self.client.session.get('otp_code')

    def test_request_otp_sends_email(self):
        code = self.request_otp()

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertIn('Your OTP Code', email.subject)
        self.assertIsNotNone(code)
        self.assertIn(code, email.body)

    @patch(
        'accounts.views.render',
        return_value=HttpResponse()
    )
    def test_wrong_otp_is_rejected(self, mock_render):
        self.request_otp()

        response = self.client.post(
            reverse('accounts:verify_otp'),
            {
                'email': 'test@example.com',
                'code': '000000',
            }
        )

        self.assertEqual(response.status_code, 200)

        session = self.client.session
        self.assertEqual(session.get('otp_attempts'), 1)

        self.assertNotIn('_auth_user_id', session)

    @patch(
        'accounts.views.render',
        return_value=HttpResponse()
    )
    def test_expired_otp_is_rejected(self, mock_render):
        code = self.request_otp()

        session = self.client.session

        session['otp_created_at'] = (
            timezone.now() - timedelta(seconds=121)
        ).isoformat()

        session.save()

        response = self.client.post(
            reverse('accounts:verify_otp'),
            {
                'email': 'test@example.com',
                'code': code,
            }
        )

        self.assertEqual(response.status_code, 200)

        session = self.client.session

        self.assertIsNone(session.get('otp_code'))
        self.assertIsNone(session.get('otp_email'))
        self.assertIsNone(session.get('otp_created_at'))

    def test_otp_can_be_used_only_once(self):
        code = self.request_otp()

        response = self.client.post(
            reverse('accounts:verify_otp'),
            {
                'email': 'test@example.com',
                'code': code,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            reverse('accounts:profile')
        )

        self.client.logout()

        session = self.client.session

        self.assertIsNone(session.get('otp_code'))

        with patch(
            'accounts.views.render',
            return_value=HttpResponse()
        ):
            response = self.client.post(
                reverse('accounts:verify_otp'),
                {
                    'email': 'test@example.com',
                    'code': code,
                }
            )

        self.assertEqual(response.status_code, 200)

    def test_otp_login_redirects_to_profile(self):
        code = self.request_otp()

        response = self.client.post(
            reverse('accounts:verify_otp'),
            {
                'email': 'test@example.com',
                'code': code,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            reverse('accounts:profile')
        )

        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )
    def test_unauthenticated_user_redirected_from_profile(self):
        response = self.client.get(
            reverse('accounts:profile')
        )

        self.assertEqual(response.status_code, 302)

        self.assertIn(
            reverse('accounts:login'),
            response.url
        )