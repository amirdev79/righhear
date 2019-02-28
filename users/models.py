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


class UserData(models.Model):
    fb_events = models.ManyToManyField(FacebookEvent)
    fb_profile_image_small = models.ImageField(editable=False, null=True)
    fb_profile_image_normal = models.ImageField(editable=False, null=True)
    fb_profile_image_large = models.ImageField(editable=False, null=True)

    def __str__(self):
        return self.userprofile.user.first_name + ' ' + self.userprofile.user.last_name + ' - ' + self.userprofile.user.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.ManyToManyField('events.EventCategory')
    preferred_sub_categories = models.ManyToManyField('events.EventSubCategory')
    preferred_language = models.CharField(max_length=3, default="he")
    fb_id = models.CharField(max_length=50, null=True)
    fb_access_token = models.CharField(max_length=500, null=True)
    user_data = models.OneToOneField(UserData, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' - ' + self.user.username


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

    def __str__(self):
        return self.user.user.username + ', ' + str(self.event.id) + ', ' + self.SWIPE_ACTION_CHOICES[self.action]
