from django.test import TestCase
from shortener.models import URL
from datetime import datetime

class URLModelTestCase(TestCase):
    def test_count_visit(self):
        # Create a URL instance for testing
        url = URL.objects.create(url='https://assetcare.nl', shortcode='asc123')

        # Call the count_visit method
        url.count_visit()

        # Retrieve the URL instance from the database
        updated_url = URL.objects.get(pk=url.pk)

        # Assert the expected changes
        self.assertIsNotNone(updated_url.last_redirect)
        self.assertEqual(updated_url.redirect_count, 1)

    

    
        


                         