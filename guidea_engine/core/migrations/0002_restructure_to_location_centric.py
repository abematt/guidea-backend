# Generated migration for restructuring to location-centric model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Step 1: Add new fields to Location model
        migrations.AddField(
            model_name='location',
            field=models.TextField(default=''),
            name='raw_text',
        ),
        migrations.AddField(
            model_name='location',
            field=models.IntegerField(default=1),
            name='version',
        ),
        migrations.AddField(
            model_name='location',
            field=models.DateTimeField(auto_now=True),
            name='updated',
        ),
        
        # Step 2: Make document field nullable temporarily to preserve data
        migrations.AlterField(
            model_name='location',
            name='document',
            field=models.ForeignKey(
                null=True, 
                blank=True, 
                on_delete=models.CASCADE, 
                related_name='locations', 
                to='core.document'
            ),
        ),
    ] 