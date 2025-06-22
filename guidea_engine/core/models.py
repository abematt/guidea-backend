from django.db import models

from django.db import models

class Document(models.Model):
    title = models.TextField()
    raw_md = models.TextField()
    version = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class Location(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='locations')
    name = models.TextField()
    latlon_json = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)

class TextSnippet(models.Model):
    LENGTH_CHOICES = [
        ('short', 'Short'),
        ('medium', 'Medium'),
        ('long', 'Long'),
    ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='text_snippets')
    length = models.CharField(max_length=10, choices=LENGTH_CHOICES)
    text = models.TextField()
    hash = models.TextField()
    is_current = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class AudioSnippet(models.Model):
    text_snippet = models.ForeignKey(TextSnippet, on_delete=models.CASCADE, related_name='audio_snippets')
    voice_id = models.TextField()
    audio_url = models.TextField()
    is_current = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

class Tour(models.Model):
    name = models.TextField()
    description = models.TextField()
    location_order_json = models.JSONField()

class StitchCache(models.Model):
    tour_id_or_hash = models.TextField()
    length = models.TextField()
    doc_version = models.IntegerField()
    audio_url = models.TextField()
    expires_at = models.DateTimeField()
