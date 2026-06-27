from django.test import TestCase
from gin_calculator import __version__


class AppVersionTest(TestCase):
    def test_version_in_context(self):
        response = self.client.get('/')
        self.assertEqual(response.context['app_version'], __version__)

    def test_version_in_footer(self):
        response = self.client.get('/')
        self.assertContains(response, f'v{__version__}')
