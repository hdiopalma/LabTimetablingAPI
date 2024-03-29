# Generated by Django 4.2.4 on 2024-03-22 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_data', '0008_remove_laboratory_assistants_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assistant',
            name='prefered_schedule',
            field=models.JSONField(default={'Friday': {'Shift1': True, 'Shift2': True, 'Shift3': True, 'Shift4': False, 'Shift5': True, 'Shift6': False}, 'Monday': {'Shift1': True, 'Shift2': True, 'Shift3': True, 'Shift4': False, 'Shift5': True, 'Shift6': False}, 'Saturday': {'Shift1': True, 'Shift2': True, 'Shift3': False, 'Shift4': False, 'Shift5': False, 'Shift6': True}, 'Thursday': {'Shift1': False, 'Shift2': False, 'Shift3': False, 'Shift4': True, 'Shift5': True, 'Shift6': False}, 'Tuesday': {'Shift1': True, 'Shift2': False, 'Shift3': False, 'Shift4': True, 'Shift5': True, 'Shift6': True}, 'Wednesday': {'Shift1': True, 'Shift2': False, 'Shift3': True, 'Shift4': True, 'Shift5': True, 'Shift6': True}}),
        ),
        migrations.AlterField(
            model_name='assistant',
            name='regular_schedule',
            field=models.JSONField(default={'Friday': {'Shift1': True, 'Shift2': True, 'Shift3': True, 'Shift4': False, 'Shift5': True, 'Shift6': False}, 'Monday': {'Shift1': True, 'Shift2': True, 'Shift3': True, 'Shift4': False, 'Shift5': True, 'Shift6': False}, 'Saturday': {'Shift1': True, 'Shift2': True, 'Shift3': False, 'Shift4': False, 'Shift5': False, 'Shift6': True}, 'Thursday': {'Shift1': False, 'Shift2': False, 'Shift3': False, 'Shift4': True, 'Shift5': True, 'Shift6': False}, 'Tuesday': {'Shift1': True, 'Shift2': False, 'Shift3': False, 'Shift4': True, 'Shift5': True, 'Shift6': True}, 'Wednesday': {'Shift1': True, 'Shift2': False, 'Shift3': True, 'Shift4': True, 'Shift5': True, 'Shift6': True}}),
        ),
        migrations.AlterField(
            model_name='participant',
            name='regular_schedule',
            field=models.JSONField(default={'Friday': {'Shift1': True, 'Shift2': True, 'Shift3': True, 'Shift4': False, 'Shift5': True, 'Shift6': False}, 'Monday': {'Shift1': True, 'Shift2': True, 'Shift3': True, 'Shift4': False, 'Shift5': True, 'Shift6': False}, 'Saturday': {'Shift1': True, 'Shift2': True, 'Shift3': False, 'Shift4': False, 'Shift5': False, 'Shift6': True}, 'Thursday': {'Shift1': False, 'Shift2': False, 'Shift3': False, 'Shift4': True, 'Shift5': True, 'Shift6': False}, 'Tuesday': {'Shift1': True, 'Shift2': False, 'Shift3': False, 'Shift4': True, 'Shift5': True, 'Shift6': True}, 'Wednesday': {'Shift1': True, 'Shift2': False, 'Shift3': True, 'Shift4': True, 'Shift5': True, 'Shift6': True}}),
        ),
    ]
