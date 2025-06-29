from django.contrib import admin
from .models import Location, TextSnippet, AudioSnippet, Tour, StitchCache

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'created', 'updated']
    list_filter = ['created', 'updated']
    search_fields = ['name']
    readonly_fields = ['created', 'updated']

@admin.register(TextSnippet)
class TextSnippetAdmin(admin.ModelAdmin):
    list_display = ['location', 'length', 'is_current', 'created']
    list_filter = ['length', 'is_current', 'created']
    search_fields = ['location__name', 'text']

@admin.register(AudioSnippet)
class AudioSnippetAdmin(admin.ModelAdmin):
    list_display = ['text_snippet', 'voice_id', 'is_current', 'created']
    list_filter = ['voice_id', 'is_current', 'created']

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'updated']
    search_fields = ['name', 'description']

admin.site.register(StitchCache)
