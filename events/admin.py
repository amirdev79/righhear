from adminsortable.admin import SortableAdmin
from django.contrib import admin

# Register your models here.,
from events.models import Event, EventCategory, EventSubCategory, Venue, Artist, Media, Audience


class ArtistAdmin(admin.ModelAdmin):
    filter_horizontal = ('media', 'sub_categories',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'create_time', 'title', 'title_heb', 'artist', 'venue', 'enabled')
    filter_horizontal = ('media', 'sub_categories',)


class MediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'type', 'link', 'youtube_id', 'playback_start', 'playback_end', 'create_time')
    list_filter = 'type',


admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory, SortableAdmin)
admin.site.register(EventSubCategory)
admin.site.register(Venue)
admin.site.register(Audience)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Media, MediaAdmin)
