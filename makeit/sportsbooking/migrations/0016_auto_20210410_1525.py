# Generated by Django 3.1.1 on 2021-04-10 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbooking', '0015_auto_20210410_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backuporder',
            name='backup_portal_pass',
            field=models.CharField(max_length=96, null=True, verbose_name='门户密码'),
        ),
    ]
