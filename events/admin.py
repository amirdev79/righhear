from django.contrib import admin

# Register your models here.,
from events.models import Event, EventCategory, EventSubCategory, Venue, Artist, UserSwipeAction, Media

class ArtistAdmin(admin.ModelAdmin):
    filter_horizontal = ('media', 'sub_categories',)

class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('media', 'sub_categories',)


admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory)
admin.site.register(EventSubCategory)
admin.site.register(Venue)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(UserSwipeAction)
admin.site.register(Media)

