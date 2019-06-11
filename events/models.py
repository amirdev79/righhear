from adminsortable.models import SortableMixin
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.db import models

from users.models import UserProfile


class EventCategory(SortableMixin):
    class Meta:
        verbose_name = 'Event Category'
        verbose_name_plural = 'Event Categories'
        ordering = ['order']

    def event_category_media_path(instance, filename):
        return 'categories/{0}_{1}.{2}'.format(instance.id, instance.title, filename[-3:])

    title = models.CharField(max_length=50)
    title_heb = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to=event_category_media_path)
    enabled = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    icon_name = models.CharField(max_length=10, null=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.title


class EventSubCategory(models.Model):
    def event_sub_category_media_path(instance, filename):
        return 'subcategories/{0}_{1}.{2}'.format(instance.id, instance.title, filename[-3:])

    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    title_heb = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to=event_sub_category_media_path)

    def __str__(self):
        return str(self.id) + ' - ' + self.title


class Venue(models.Model):
    name = models.CharField(max_length=50)
    name_heb = models.CharField(max_length=50, null=True)
    street_address = models.CharField(max_length=200)
    street_address_heb = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=50)
    city_heb = models.CharField(max_length=50, null=True)
    link = models.URLField(blank=True, max_length=400)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, editable=True, blank=False, default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, editable=True, blank=False, default=0)
    location = PointField(null=True, blank=True, srid=4326, verbose_name="Location")
    additional_info = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Do the maths here to calculate lat/lon
        self.location = Point(x=float(self.longitude), y=float(self.latitude), srid=4326)
        super(Venue, self).save(*args, **kwargs)

    def __str__(self):
        return '%d - %s - %s (%s - %s)' % (self.id, self.name, self.city or '', self.name_heb, self.city_heb or '')
        return str(self.id) + self.name + ' - ' + (self.city or '') + ' (' + (self.name_heb or '') + ' - ' + (
                self.city_heb or '') + ')'


class Media(models.Model):

    def thumbnail_media_path(instance, filename):
        return 'media_thumbnails/{0}/{1}'.format(instance.id if instance.id else 'new', filename)

    TYPE_IMAGE, TYPE_AUDIO, TYPE_VIDEO, TYPE_YOUTUBE = "IMG", "AUD", "VID", "YT"
    MEDIA_TYPE_CHOICES = {
        TYPE_IMAGE: "Image",
        TYPE_AUDIO: "Audio",
        TYPE_VIDEO: "Video",
        TYPE_YOUTUBE: "Youtube"
    }

    SOURCE_EVENT, SOURCE_ARTIST = "SRC_EVENT", "SRC_ARTIST"
    MEDIA_SOURCE_CHOICES = {
        SOURCE_EVENT: "Event",
        SOURCE_ARTIST: "Artist"
    }

    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=3, choices=MEDIA_TYPE_CHOICES.items(), default=TYPE_IMAGE)
    source = models.CharField(max_length=10, choices=MEDIA_SOURCE_CHOICES.items(), default=SOURCE_ARTIST)
    tag = models.CharField(max_length=100, null=False, blank=False)
    link = models.URLField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to=thumbnail_media_path, blank=True)
    youtube_id = models.CharField(max_length=20, null=True, blank=True)
    playback_start = models.IntegerField(blank=True, null=True)
    playback_end = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.tag


class Artist(models.Model):
    def artist_media_path(instance, filename):
        return 'artists/{0}/{1}'.format(instance.id if instance.id else 'new', filename)

    first_name = models.CharField(max_length=50)
    first_name_heb = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, null=True, blank=True)
    last_name_heb = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to=artist_media_path, blank=True)
    image_credits = models.CharField(max_length=500, null=True, blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True)
    sub_categories = models.ManyToManyField(EventSubCategory)
    media = models.ManyToManyField(Media, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + (self.first_name or '') + ' ' + (self.last_name or '')


class Audience(models.Model):

    def audiences_media_path(instance, filename):
        return 'audiences/{0}/{1}'.format(instance.id if instance.id else 'new', filename)

    title = models.CharField(db_index=True, max_length=50)
    title_heb = models.CharField(db_index=True, max_length=50, null=True)
    icon = models.ImageField(upload_to=audiences_media_path, blank=True, null=True)

    def __str__(self):
        return '%d - %s (%s)' % (self.id, self.title or '', self.title_heb or '')


class Event(models.Model):

    def events_media_path(instance, filename):
        return 'events/{0}/{1}'.format(instance.id if instance.id else 'new', filename)

    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    categories = models.ManyToManyField(EventCategory)
    sub_categories = models.ManyToManyField(EventSubCategory)
    title = models.CharField(db_index=True, max_length=50, blank=True)
    title_heb = models.CharField(db_index=True, max_length=50, blank=True)
    short_description = models.CharField(max_length=200, blank=True)
    short_description_heb = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    description_heb = models.CharField(max_length=1000, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True, blank=True)
    promotion = JSONField(null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    media = models.ManyToManyField(Media, blank=True)
    enabled = models.BooleanField(default=True)
    image = models.ImageField(upload_to=events_media_path, null=True, blank=True)
    audiences = models.ManyToManyField(Audience)
    rating = models.IntegerField(default=0)
    tickets_link = models.URLField(blank=True)
    additional_info = JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.title or '' + ', ' + self.title_heb or ''
