# Generated by Django 3.1.1 on 2021-04-10 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_backupuser'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BackUpUser',
        ),
    ]
