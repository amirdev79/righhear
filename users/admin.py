from django.contrib import admin

from users.models import UserProfile, UserDevice, UserSwipeAction, UserData, UserMessage


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'os', 'os_version', 'model', 'timezone', 'last_login')


class UserSwipeActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'action', 'lng', 'lat')


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_language', 'fb_id')


class UserDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'fb_profile_image_small', 'fb_profile_image_normal', 'fb_profile_image_large')

class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'text')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(UserData, UserDataAdmin)
admin.site.register(UserDevice, UserDeviceAdmin)
admin.site.register(UserSwipeAction, UserSwipeActionAdmin)
admin.site.register(UserMessage, UserMessageAdmin)
