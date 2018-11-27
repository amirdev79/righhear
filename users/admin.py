from django.contrib import admin
from users.models import UserProfile, UserDevice, UserSwipeAction


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'os', 'os_version', 'model', 'timezone', 'last_login')


class UserSwipeActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'action')

admin.site.register(UserProfile)
admin.site.register(UserDevice, UserDeviceAdmin)
admin.site.register(UserSwipeAction, UserSwipeActionAdmin)

