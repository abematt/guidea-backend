from django.db import models


class Location(models.Model):
    name = models.TextField()
    raw_text = models.TextField()
    version = models.IntegerField(default=1)
    latlon_json = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return f"{self.location.name} - {self.length}"


class AudioSnippet(models.Model):
    text_snippet = models.ForeignKey(TextSnippet, on_delete=models.CASCADE, related_name='audio_snippets')
    voice_id = models.TextField()
    audio_url = models.TextField()
    is_current = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Audio for {self.text_snippet}"


class Tour(models.Model):
    name = models.TextField()
    description = models.TextField()
    location_order_json = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class StitchCache(models.Model):
    tour_id_or_hash = models.TextField()
    length = models.TextField()
    location_versions_hash = models.TextField()  # Track version changes across locations
    audio_url = models.TextField()
    expires_at = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cache for tour {self.tour_id_or_hash}"
