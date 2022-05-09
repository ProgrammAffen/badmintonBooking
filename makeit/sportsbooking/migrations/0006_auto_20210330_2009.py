# Generated by Django 3.1.1 on 2021-03-30 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0022_auto_20210330_1953'),
        ('sportsbooking', '0005_auto_20210330_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderprofile',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_user_id', to='user.userprofile'),
        ),
    ]