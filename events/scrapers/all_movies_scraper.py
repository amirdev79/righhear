import email
import tempfile
from itertools import cycle

import requests
from bs4 import BeautifulSoup

from righthear import settings
from django.core.mail import EmailMessage

from events.models import Venue
from events.scrapers.common import wait, get_proxies
from events.utils import get_gmaps_info

ALL_MOVIES_URL = 'http://allmovies.co.il/'


def get_movies():

    return;