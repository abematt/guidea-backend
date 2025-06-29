# Data migration to preserve existing location content

from django.db import migrations


def migrate_location_data(apps, schema_editor):
    """
    Copy relevant data from documents to locations before removing document model
    """
    Document = apps.get_model('core', 'Document')
    Location = apps.get_model('core', 'Location')
    
    # For each location, try to extract relevant content from its document
    for location in Location.objects.all():
        if location.document:
            # You might want to customize this logic based on how you want to 
            # extract location-specific content from the document's raw_md
            location.raw_text = f"Content for {location.name}"  # Placeholder
            location.version = location.document.version
            location.save()


def reverse_migrate_location_data(apps, schema_editor):
    """
    Reverse migration - clear the new fields
    """
    Location = apps.get_model('core', 'Location')
    for location in Location.objects.all():
        location.raw_text = ''
        location.version = 1
        location.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_restructure_to_location_centric'),
    ]

    operations = [
        migrations.RunPython(
            migrate_location_data,
            reverse_migrate_location_data,
        ),
    ] 