from django.db import models
from django.contrib.postgres.fields import JSONField

from users.models import UserProfile


class EventCategory(models.Model):
    def event_category_media_path(instance, filename):
        return 'categories/{0}_{1}.{2}'.format(instance.id, instance.title, filename[-3:])

    title = models.CharField(max_length=20)
    image = models.ImageField(upload_to=event_category_media_path)

    def __str__(self):
        return self.title


class EventSubCategory(models.Model):
    def event_sub_category_media_path(instance, filename):
        return 'subcategories/{0}_{1}.{2}'.format(instance.id, instance.title, filename[-3:])

    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    image = models.ImageField(upload_to=event_sub_category_media_path)

    def __str__(self):
        return self.title


class Venue(models.Model):
    name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    link = models.URLField(blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name + ' - ' + self.city


class Media(models.Model):
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

    def __str__(self):
        return self.link[self.link.rfind('/')+1:] + ' (' +self.type + ')'


class Artist(models.Model):
    def artist_media_path(instance, filename):
        return 'artists/{0}/{1}'.format(instance.id if instance else 'new', filename)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to=artist_media_path, blank=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True)
    media = models.ManyToManyField(Media, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.first_name + ' ' + self.last_name


class Event(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True)
    sub_category = models.ForeignKey(EventSubCategory, on_delete=models.SET_NULL, null=True)
    title = models.CharField(db_index=True, max_length=200, blank=True)
    short_description = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    promotion = JSONField(null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True)
    media = models.ManyToManyField(Media, blank=True)

    def __str__(self):
        return self.title + ' (' + self.category.title + ')' + ' - ' + self.venue.name


class UserSwipeAction(models.Model):
    TYPE_LEFT, TYPE_TOP, TYPE_RIGHT, TYPE_BOTTOM = 'LEFT', 'TOP', 'RIGHT', 'BOTTOM'

    SWIPE_ACTION_TYPE_CHOICES = {
        TYPE_LEFT: "Left",
        TYPE_TOP: "Top",
        TYPE_RIGHT: "Right",
        TYPE_BOTTOM: "Bottom",
    }

    action_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=6, choices=SWIPE_ACTION_TYPE_CHOICES.items(), default=TYPE_LEFT)



    # create_time: datetime
    # created_by - UserProfile
    # category: EventCategory
    # sub_cateogry: EventSubCategory
    # title: text
    # description: text
    # artist: Artist
    # price: number
    # start_time: datetime
    # end_time: datetime
    # promotion: Many
    # to
    # Many
    # EventPromotion
    # venue: FK
    # Venue ==
    # media: Many
    # to
    # Many
    # Media
