from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_categories = models.ManyToManyField('events.EventCategory');
    preferred_sub_categories = models.ManyToManyField('events.EventSubCategory');

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name + ' - ' + self.user.username


