# Generated by Django 5.0.3 on 2024-04-13 16:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduling_data', '0011_participant_ipk'),
    ]

    operations = [
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('start_time', models.DateTimeField(auto_now_add=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='Pending', max_length=32)),
                ('iteration_log', models.JSONField(default=list)),
                ('fitness', models.JSONField(default=dict)),
                ('selection', models.JSONField(default=dict)),
                ('crossover', models.JSONField(default=dict)),
                ('mutation', models.JSONField(default=dict)),
                ('repair', models.JSONField(default=dict)),
                ('neighborhood', models.JSONField(default=dict)),
                ('algorithm', models.JSONField(default=dict)),
                ('local_search', models.JSONField(default=dict)),
                ('max_iteration', models.IntegerField(default=500)),
                ('population_size', models.IntegerField(default=25)),
                ('elitism_size', models.IntegerField(default=2)),
                ('best_fitness', models.FloatField(blank=True, null=True)),
                ('time_elapsed', models.FloatField(blank=True, null=True)),
                ('best_solution', models.JSONField(blank=True, null=True)),
                ('gene_count', models.IntegerField(blank=True, null=True)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='scheduling_data.semester')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('day_of_week', models.CharField(max_length=10)),
                ('shift', models.CharField(max_length=10)),
                ('time_slot', models.JSONField(default=dict)),
                ('assistant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='scheduling_data.assistant')),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='scheduling_data.chapter')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='scheduling_data.group')),
                ('laboratory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='scheduling_data.laboratory')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedules', to='scheduling_data.module')),
                ('process_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='schedule_data', to='scheduling_data.solution')),
            ],
        ),
    ]
