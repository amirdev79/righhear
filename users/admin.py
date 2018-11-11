from django.contrib import admin
from users.models import UserProfile, UserDevice


class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_id', 'os', 'os_version', 'model', 'timezone', 'last_login')

admin.site.register(UserProfile)
admin.site.register(UserDevice, UserDeviceAdmin)
