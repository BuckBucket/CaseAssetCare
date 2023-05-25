import json
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from rest_framework import status
from shortener.models import URL
from shortener.views import ShortenView, StatsView
from django.utils.timezone import make_aware

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        
    def test_shortenview_correct_POST(self):
        url = reverse('shorten-view')
        data = {
            'url': 'https://assetcare.nl',
            'shortcode': 'asc123'
        }
        request = self.factory.post(url, data)
        response = ShortenView.as_view()(request)
        self.assertEqual(response.status_code, 201)

    def test_shortenview_no_url_POST(self):
        url = reverse('shorten-view')
        data = {
            'shortcode': 'asc123'
        }
        request = self.factory.post(url, data)
        response = ShortenView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_shortenview_invalid_shortcode_POST(self):
        url = reverse('shorten-view')
        data = {
            'url': 'https://assetcare.nl',
            'shortcode': 'abc!@#'
        }
        request = self.factory.post(url, data)
        response = ShortenView.as_view()(request)
        self.assertEqual(response.status_code, 412)

    def test_shortenview_shortcode_in_use_POST(self):
        # Create a URL instance with the same shortcode for testing
        URL.objects.create(url='https://assetcare.nl', shortcode='asc123')

        url = reverse('shorten-view')
        data = {
            'url': 'https://assetcare.nl',
            'shortcode': 'asc123'
        }
        request = self.factory.post(url, data)
        response = ShortenView.as_view()(request)
        self.assertEqual(response.status_code, 409)


class RedirectViewTestCase(TestCase):
    def test_get_existing_shortcode(self):
        # Create a URL instance for testing
        url = URL.objects.create(url='https://assetcare.nl', shortcode='asc123')

        redirect_url = reverse('redirect-view', args=[url.shortcode])
        response = self.client.get(redirect_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url.url)

    def test_get_nonexistent_shortcode(self):
        redirect_url = reverse('redirect-view', args=['nonexistent'])
        response = self.client.get(redirect_url)
        self.assertEqual(response.status_code, 404)


class StatsViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get_existing_shortcode(self):
        # Create a URL instance for testing
        url = URL.objects.create(url='https://assetcare.nl', shortcode='asc123')

        stats_url = reverse('stats-view', args=[url.shortcode])
        request = self.factory.get(stats_url)
        response = StatsView.as_view()(request, shortcode=url.shortcode)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Render the response content
        response.render() # type: ignore

        # Parse the JSON response
        response_data = json.loads(response.content)

        # Assert specific values in the response data and fix the expected_created value
        expected_created = url.created.isoformat()[:-6] + 'Z'
        self.assertEqual(response_data['created'], expected_created)
        self.assertEqual(response_data['last_redirect'], url.last_redirect)
        self.assertEqual(response_data['redirect_count'], url.redirect_count)

    def test_get_nonexistent_shortcode(self):
        stats_url = reverse('stats-view', args=['nonexistent'])
        response = self.client.get(stats_url)
        self.assertEqual(response.status_code, 404)
