# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-11-01 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_app', '0004_userprofileinfo_date_of_birth'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.IntegerField(primary_key=True, serialize=False)),
                ('session_name', models.CharField(max_length=80)),
                ('course_title', models.CharField(max_length=80)),
                ('credit_hour', models.IntegerField()),
            ],
            options={
                'db_table': 'course',
            },
        ),
    ]
