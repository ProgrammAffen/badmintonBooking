# Generated by Django 3.1.1 on 2021-03-16 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0013_auto_20210316_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(max_length=32, null=True, unique=True, verbose_name='邮箱'),
        ),
    ]