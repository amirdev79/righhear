from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models


class FacebookEvent(models.Model):
    fb_id = models.CharField(max_length=50)
    description = models.CharField(max_length=10000)
    name = models.CharField(max_length=100)
    start_time = models.DateTimeField(editable=False)
    end_time = models.DateTimeField(editable=False, null=True)
    rsvp_status = models.CharField(max_length=20)
    place = JSONField()


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.ManyToManyField('events.EventCategory')
    preferred_sub_categories = models.ManyToManyField('events.EventSubCategory')
    preferred_language = models.CharField(max_length=3, default="he")
    fb_id = models.CharField(max_length=50, null=True)
    fb_access_token = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' - ' + self.user.username


class UserData(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, null=True)
    fb_events = models.ManyToManyField(FacebookEvent)
    fb_profile_image_small = models.ImageField(editable=False, null=True)
    fb_profile_image_normal = models.ImageField(editable=False, null=True)
    fb_profile_image_large = models.ImageField(editable=False, null=True)

    def __str__(self):
        return self.user.user.first_name + ' ' + self.user.user.last_name + ' - ' + self.user.user.username


class UserDevice(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50, editable=False)
    os = models.CharField(max_length=20, null=True, editable=False, blank=True)
    os_version = models.CharField(max_length=20, null=True, editable=False, blank=True)
    timezone = models.CharField(max_length=50, null=True, editable=False, blank=True)
    model = models.CharField(max_length=50, null=True, editable=False, blank=True)
    push_token = models.CharField(max_length=256, unique=True, editable=False, blank=True)
    last_login = models.DateTimeField(editable=False, blank=True)

    def __str__(self):
        return self.user.username + ' ' + self.device_id + ' - '


class UserSwipeAction(models.Model):
    ACTION_UP, ACTION_LEFT, ACTION_DOWN, ACTION_RIGHT = 0, 1, 2, 3  # must match client code in SwipeHandler.java

    SWIPE_ACTION_CHOICES = {
        ACTION_LEFT: 'LEFT',
        ACTION_UP: 'UP',
        ACTION_RIGHT: 'RIGHT',
        ACTION_DOWN: 'DOWN',
    }

    action_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True)
    action = models.IntegerField(choices=SWIPE_ACTION_CHOICES.items(), default=ACTION_LEFT)
    lng =  models.DecimalField(max_digits=9, decimal_places=6, editable=False, default=0)
    lat =  models.DecimalField(max_digits=9, decimal_places=6, editable=False, default=0)

    def __str__(self):
        return self.user.user.username + ', ' + str(self.event.id) + ', ' + self.SWIPE_ACTION_CHOICES[self.action]


class UserRelations(models.Model):
    RELATION_FRIEND, = 0,
    RELATION_CHOICES = {
        RELATION_FRIEND: 'Friend',
    }

    STATE_PENDING, STATE_CONNECTED = 0, 1
    STATE_CHOICES = {
        STATE_PENDING: 'Pending',
        STATE_CONNECTED: 'Connected'
    }

    relating_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_relations_relating')
    related_user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='user_relations_related')
    relation = models.IntegerField(choices=RELATION_CHOICES.items(), default=RELATION_FRIEND)
    state = models.IntegerField(choices=STATE_CHOICES.items(), default=STATE_PENDING)
    meta_data = JSONField(null=True, blank=True, editable=False)