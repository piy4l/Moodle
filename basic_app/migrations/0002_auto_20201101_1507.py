# Generated by Django 3.1.2 on 2020-11-01 09:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='portfolio_site',
        ),
        migrations.RemoveField(
            model_name='userprofileinfo',
            name='profile_pic',
        ),
    ]
