# Generated by Django 3.1.1 on 2021-03-30 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbooking', '0008_auto_20210331_0011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderprofile',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
