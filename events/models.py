from django.db import models
from django.contrib.postgres.fields import JSONField

from users.models import UserProfile


class EventCategory(models.Model):
    def event_category_media_path(instance, filename):
        return 'categories/{0}_{1}.{2}'.format(instance.id, instance.title, filename[-3:])

    title = models.CharField(max_length=50)
    title_heb = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to=event_category_media_path)

    def __str__(self):
        return self.title


class EventSubCategory(models.Model):
    def event_sub_category_media_path(instance, filename):
        return 'subcategories/{0}_{1}.{2}'.format(instance.id, instance.title, filename[-3:])

    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to=event_sub_category_media_path)

    def __str__(self):
        return self.title


class Venue(models.Model):
    name = models.CharField(max_length=50)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    link = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, editable=False, default=0)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, editable=False, default=0)

    def __str__(self):
        return self.name + ' - ' + self.city


class Media(models.Model):

    def thumbnail_media_path(instance, filename):
        return 'media_thumbnails/{0}/{1}'.format(instance.id if instance.id else 'new', filename)


    TYPE_IMAGE, TYPE_AUDIO, TYPE_VIDEO = "IMG", "AUD", "VID"
    MEDIA_TYPE_CHOICES = {
        TYPE_IMAGE: "Image",
        TYPE_AUDIO: "Audio",
        TYPE_VIDEO: "Video",
    }

    SOURCE_EVENT, SOURCE_ARTIST = "SRC_EVENT", "SRC_ARTIST"
    MEDIA_SOURCE_CHOICES = {
        SOURCE_EVENT: "Event",
        SOURCE_ARTIST: "Artist"
    }

    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=3, choices=MEDIA_TYPE_CHOICES.items(), default=TYPE_IMAGE)
    source = models.CharField(max_length=10, choices=MEDIA_SOURCE_CHOICES.items(), default=SOURCE_EVENT)
    link = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to=thumbnail_media_path, blank=True)


    def __str__(self):
        return self.link[self.link.rfind('/')+1:] + ' (' +self.type + ')'


class Artist(models.Model):
    def artist_media_path(instance, filename):
        return 'artists/{0}/{1}'.format(instance.id if instance.id else 'new', filename)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to=artist_media_path, blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True)
    sub_categories = models.ManyToManyField(EventSubCategory)
    media = models.ManyToManyField(Media, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.first_name + ' ' + self.last_name or ''


class Audience(models.Model):

    def audiences_media_path(instance, filename):
        return 'audiences/{0}/{1}'.format(instance.id if instance.id else 'new', filename)

    title = models.CharField(db_index=True, max_length=50)
    title_heb = models.CharField(db_index=True, max_length=50, null=True)
    icon = models.ImageField(upload_to=audiences_media_path, blank=True, null=True)


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
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)
    price = models.IntegerField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    promotion = JSONField(null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    media = models.ManyToManyField(Media, blank=True)
    enabled = models.BooleanField(default=True)
    image = models.ImageField(upload_to=events_media_path, blank=True)
    audiences = models.ManyToManyField(Audience)


    def __str__(self):
        return self.title #+ ' (' + self.category.title + ')' + ' - ' + self.venue.name

