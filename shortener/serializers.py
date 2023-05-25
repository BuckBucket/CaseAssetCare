import string
import random
from rest_framework import serializers
from .models import URL
from .exceptions import InvalidShortcodeException, ShortcodeInUseException

class UrlStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = URL
        fields = ("created", "last_redirect", "redirect_count")


class CreateUrlSerializer(serializers.Serializer):
    """
    Serializer for creating a shortened URL.

    This serializer is used to validate and create a shortened URL. It accepts the following fields:
        - url: The original URL to be shortened (required)
        - shortcode: The custom shortcode for the shortened URL (optional)

    The `validate_shortcode` method validates the provided shortcode and generates a random one if not provided.
    It checks if the shortcode is alphanumeric, contains only lowercase letters, digits, and underscores,
    and has a length of 6 characters. If the shortcode is already in use, a `ShortcodeInUseException` is raised.

    The `create` method creates a new URL object using the validated data.

    Example Usage:
        serializer = CreateUrlSerializer(data={"url": "https://assetcare.nl", "shortcode": "asc123"})
        if serializer.is_valid():
            url = serializer.create(serializer.validated_data)
            # Process the created URL object

    """

    url = serializers.URLField(required=True)
    shortcode = serializers.CharField(required=False)

    def validate_shortcode(self, value):
        # Validate and generate shortcode if not provided
        if not value:
            value = "".join(
                random.choice(string.ascii_lowercase + string.digits + "_")
                for _ in range(6)
            )
        else:
            value = value.lower()
            if not value.replace("_", "").isalnum() or len(value) != 6:
                raise InvalidShortcodeException
            if URL.objects.filter(shortcode=value).exists():
                raise ShortcodeInUseException
        return value

    def create(self, validated_data):
        # Create a new URL object
        return URL.objects.create(
            url=validated_data["url"], shortcode=validated_data["shortcode"]
        )
