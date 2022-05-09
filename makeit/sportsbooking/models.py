from django.db import models
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from user.models import UserProfile


# Create your models here.
class OrderProfile(models.Model):
    order_no = models.CharField(max_length=32,verbose_name="订单号",null=True)
    sports_type = models.CharField(max_length=16,verbose_name="场地类型",null=True)
    order_date = models.DateTimeField(verbose_name="订单时间",null=True)
    booking_date = models.DateField(verbose_name="预订时间",null=True)
    booking_weekday = models.IntegerField(verbose_name="订单星期数",null=True)
    order_coordinate = models.CharField(max_length=32,verbose_name="预订场地",null=True)
    payment = models.FloatField(verbose_name="应付金额",null=True)
    order_status = models.CharField(verbose_name="订单状态",max_length=32,default="unstarted")
    payment_status = models.BooleanField(verbose_name="支付状态",default=0)
    user_id = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name="order_user_id")
    is_use_free = models.BooleanField(verbose_name="是否使用免费次数",default=0)

    class Meta:
        db_table = "order_profile"

class BackUpOrder(models.Model):
    booking_date = models.DateField(verbose_name="预订时间", null=True)
    order_coordinate = models.CharField(max_length=96, verbose_name="预订场地", null=True)
    backup_user = models.CharField(max_length=12, verbose_name="学号", null=True)
    backup_portal_pass = models.CharField(max_length=32,verbose_name="门户密码",null=True)
    compensate_to = models.CharField(max_length=32, verbose_name="补偿用户", null=True)
    backup_user_payment = models.CharField(max_length=32,verbose_name="支付方式",null=True)

    class Meta:
        db_table = "backup_order"

