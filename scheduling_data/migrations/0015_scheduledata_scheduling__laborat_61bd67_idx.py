# Generated by Django 5.0.3 on 2024-04-30 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_data', '0014_remove_scheduledata_process_data_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='scheduledata',
            index=models.Index(fields=['laboratory', 'module', 'chapter', 'group', 'assistant'], name='scheduling__laborat_61bd67_idx'),
        ),
    ]
