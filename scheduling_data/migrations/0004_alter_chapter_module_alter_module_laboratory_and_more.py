# Generated by Django 4.2.4 on 2024-01-31 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_data', '0003_alter_assistant_laboratory_alter_assistant_semester_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='scheduling_data.module'),
        ),
        migrations.AlterField(
            model_name='module',
            name='laboratory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='scheduling_data.laboratory'),
        ),
        migrations.AlterField(
            model_name='module',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='scheduling_data.semester'),
        ),
        migrations.AlterField(
            model_name='participant',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='scheduling_data.semester'),
        ),
    ]