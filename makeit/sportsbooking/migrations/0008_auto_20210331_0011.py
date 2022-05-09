# Generated by Django 3.1.1 on 2021-03-30 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsbooking', '0007_auto_20210330_2342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderprofile',
            name='booking_date',
            field=models.DateField(null=True, verbose_name='预订时间'),
        ),
        migrations.AlterField(
            model_name='orderprofile',
            name='booking_weekday',
            field=models.IntegerField(null=True, verbose_name='订单星期数'),
        ),
        migrations.AlterField(
            model_name='orderprofile',
            name='id',
            field=models.IntegerField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='orderprofile',
            name='order_coordinate',
            field=models.CharField(max_length=32, null=True, verbose_name='预订场地'),
        ),
        migrations.AlterField(
            model_name='orderprofile',
            name='order_date',
            field=models.DateTimeField(null=True, verbose_name='订单时间'),
        ),
        migrations.AlterField(
            model_name='orderprofile',
            name='order_no',
            field=models.CharField(max_length=32, null=True, verbose_name='订单号'),
        ),
        migrations.AlterField(
            model_name='orderprofile',
            name='payment',
            field=models.IntegerField(null=True, verbose_name='应付金额'),
        ),
        migrations.AlterField(
            model_name='orderprofile',
            name='sports_type',
            field=models.CharField(max_length=16, null=True, verbose_name='场地类型'),
        ),
    ]