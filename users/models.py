from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.ManyToManyField('events.EventCategory')
    preferred_sub_categories = models.ManyToManyField('events.EventSubCategory')

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
    ACTION_LEFT, ACTION_UP, ACTION_RIGHT, ACTION_DOWN = 'LEFT', 'UP', 'RIGHT', 'DOWN'

    SWIPE_ACTION_CHOICES = {
        ACTION_LEFT: "LEFT",
        ACTION_UP: "UP",
        ACTION_RIGHT: "RIGHT",
        ACTION_DOWN: "DOWN",
    }

    action_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=6, choices=SWIPE_ACTION_CHOICES.items(), default=ACTION_LEFT)

    def __str__(self):
        return self.user.usernname + ', ' + str(self.event.id) + ', ' + self.action
