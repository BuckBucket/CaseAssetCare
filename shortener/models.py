from django.db import models
from datetime import datetime
from django_extensions.db.models import TimeStampedModel
from django.utils.timezone import make_aware

class URL(TimeStampedModel):
    """
    Model representing a shortened URL.

    This model stores information about a shortened URL, including the original URL,
    a unique shortcode, the timestamp of the last redirect, and the count of redirects.

    Fields:
        - url: The original URL (required)
        - shortcode: The unique shortcode for the shortened URL (max length: 50, unique) (required)
        - last_redirect: The timestamp of the last redirect (nullable)
        - redirect_count: The count of redirects (default: 0)

    The `count_visit` method is used to update the `last_redirect` timestamp and increment the `redirect_count`
    when a redirect occurs. It saves the updated object.

    Example Usage:
        url = URL.objects.create(url="https://assetcare.nl", shortcode="asc123")
        url.count_visit()
        url.save()

    """

    url = models.URLField()
    shortcode = models.CharField(max_length=50, unique=True)
    last_redirect = models.DateTimeField(null=True, blank=True)
    redirect_count = models.PositiveIntegerField(default=0)

    def count_visit(self):
        # Update last_redirect timestamp and increment redirect_count
        self.last_redirect = make_aware(datetime.now())
        self.redirect_count = models.F("redirect_count") + 1
        self.save()
