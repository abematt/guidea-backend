from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_migrate_location_data'),
    ]

    operations = [
        # Remove document foreign key from Location
        migrations.RemoveField(
            model_name='location',
            name='document',
        ),
        
        # Remove Document model entirely
        migrations.DeleteModel(
            name='Document',
        ),
        
        # Update StitchCache to remove doc_version reference
        migrations.RemoveField(
            model_name='stitchcache',
            name='doc_version',
        ),
        migrations.AddField(
            model_name='stitchcache',
            name='location_versions_hash',
            field=models.TextField(default=''),
        ),
    ] 