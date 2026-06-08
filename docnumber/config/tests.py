"""Tests for project-level Django entry points."""
from django.core.handlers.wsgi import WSGIHandler
from django.test import SimpleTestCase

from config.wsgi import application


class WsgiApplicationTests(SimpleTestCase):
    """Validate the configured WSGI application object."""

    def test_wsgi_application_is_exported(self):
        """The WSGI module exposes Django's callable application object."""
        self.assertIsInstance(application, WSGIHandler)
