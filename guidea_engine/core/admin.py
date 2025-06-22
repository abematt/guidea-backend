from django.contrib import admin
from .models import Document, Location, TextSnippet, AudioSnippet, Tour, StitchCache

admin.site.register(Document)
admin.site.register(Location)
admin.site.register(TextSnippet)
admin.site.register(AudioSnippet)
admin.site.register(Tour)
admin.site.register(StitchCache)
