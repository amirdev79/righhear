from django.contrib import admin

# Register your models here.
from events.models import Event, EventCategory, EventSubCategory, Venue, Artist, EventPromotion, UserSwipeAction, Media

admin.site.register(Event)
admin.site.register(EventCategory)
admin.site.register(EventSubCategory)
admin.site.register(Venue)
admin.site.register(Artist)
admin.site.register(EventPromotion)
admin.site.register(UserSwipeAction)
admin.site.register(Media)

