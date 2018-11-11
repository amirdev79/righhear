from django.contrib import admin
from users.models import UserProfile, UserDevice

admin.site.register(UserProfile)
admin.site.register(UserDevice)
