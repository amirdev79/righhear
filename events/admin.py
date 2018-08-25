from django.contrib import admin

# Register your models here.
from events.models import Event, EventCategory, EventSubCategory, Venue, Artist, EventPromotion, UserSwipeAction, Media

class ArtistAdmin(admin.ModelAdmin):
    filter_horizontal = ('media',)

class EventAdmin(admin.ModelAdmin):
    filter_horizontal = ('media',)


admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory)
admin.site.register(EventSubCategory)
admin.site.register(Venue)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(EventPromotion)
admin.site.register(UserSwipeAction)
admin.site.register(Media)

