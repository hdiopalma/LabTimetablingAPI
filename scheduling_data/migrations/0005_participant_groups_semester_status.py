# Generated by Django 4.2.4 on 2024-02-19 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_data', '0004_alter_chapter_module_alter_module_laboratory_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='groups',
            field=models.ManyToManyField(related_name='participants', through='scheduling_data.GroupMembership', to='scheduling_data.group'),
        ),
        migrations.AddField(
            model_name='semester',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
