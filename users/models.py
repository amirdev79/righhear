from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.ManyToManyField('events.EventCategory');
    preferred_sub_categories = models.ManyToManyField('events.EventSubCategory');

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' - ' + self.user.username


class UserDevice(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50)
    os = models.CharField(max_length=20, null=True)
    os_version = models.CharField(max_length=20, null=True)
    timezone = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)
    push_token = models.CharField(max_length=256, unique=True)
    last_login = models.DateTimeField()
