# Generated by Django 4.2.4 on 2024-03-19 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_data', '0007_remove_module_semester_laboratory_semester'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='laboratory',
            name='assistants_count',
        ),
        migrations.RemoveField(
            model_name='laboratory',
            name='groups_count',
        ),
        migrations.RemoveField(
            model_name='laboratory',
            name='modules_count',
        ),
        migrations.RemoveField(
            model_name='laboratory',
            name='participants_count',
        ),
        migrations.AlterField(
            model_name='laboratory',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='laboratories', to='scheduling_data.semester'),
        ),
    ]