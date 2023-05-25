from django.http import HttpResponseRedirect
from .models import URL
from .serializers import UrlStatsSerializer, CreateUrlSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins, generics
from django.shortcuts import get_object_or_404
from .exceptions import NoShortcodeException, ShortcodeInUseException, InvalidShortcodeException


class ShortenView(generics.GenericAPIView, mixins.CreateModelMixin):
    """
    API view for shortening URLs.

    This view accepts a POST request with a JSON body containing the URL to be shortened.
    It creates a new URL instance with a generated shortcode and saves it to the database.

    Endpoint: /shorten/

    HTTP Methods:
        - POST: Shorten a URL

    Error Responses:
        - 404: Shortcode not found
        - 409: Shortcode already in use
        - 412: Invalid shortcode

    Serializer: CreateUrlSerializer

    Example Request Body:
        {
            "url": "https://assetcare.nl"
        }

    Example Response:
        {
            "url": "https://assetcare.nl",
            "shortcode": "asc123"
        }
    """
    serializer_class = CreateUrlSerializer

    def post(self, request, *args, **kwargs):
        """
        Create a shortened URL.
        """
        try:
            return self.create(request, *args, **kwargs)
        except NoShortcodeException:
            return Response("Shortcode not found", status=404)
        except ShortcodeInUseException:
            return Response("Shortcode is already in use", status=409)
        except InvalidShortcodeException:
            return Response(
                "Shortcode must be a alphanumeric code of 6 characters/numbers",
                status=412,
            )

class RedirectView(APIView):
    """
    API view for redirecting to the original URL.

    This view handles GET requests with a shortcode parameter. It retrieves the URL
    associated with the provided shortcode from the database, increments the redirect count,
    and redirects the user to the original URL.

    Endpoint: /<shortcode>/

    HTTP Methods:
        - GET: Redirect to the original URL

    Example Redirect:
        If the shortcode is "asc123" and the associated URL is "https://assetcare.nl",
        accessing "/asc123/" will redirect the user to "https://assetcare.nl".
    """
    
    def get(self, request, shortcode):
        """
        Redirect to the original URL.
        """
        url = get_object_or_404(URL, shortcode=shortcode)
        url.count_visit()
        return HttpResponseRedirect(redirect_to=url.url)


class StatsView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    """
    API view for retrieving statistics of a shortened URL.

    This view handles GET requests with a shortcode parameter. It retrieves the URL
    associated with the provided shortcode from the database and returns its statistics,
    including the creation date, last redirect date, and redirect count.

    Endpoint: /stats/<shortcode>/

    HTTP Methods:
        - GET: Retrieve statistics of a shortened URL

    Serializer: UrlStatsSerializer

    Example Response:
        {
            "created": "2023-05-25T12:00:00Z",
            "last_redirect": "2023-05-25T13:30:00Z",
            "redirect_count": 10
        }
    """

    queryset = URL.objects.all()
    serializer_class = UrlStatsSerializer
    lookup_field = "shortcode"

    def get(self, request, *args, **kwargs):
        """
        Retrieve statistics of a shortened URL.
        """
        return self.retrieve(request, *args, **kwargs)
