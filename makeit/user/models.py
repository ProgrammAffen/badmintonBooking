from django.db import models

# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=11, verbose_name='用户名')
    gender = models.CharField(max_length=4,verbose_name='性别',null=True)
    uni = models.CharField(max_length=32,verbose_name='毕业/就读院校',default='')
    fach = models.CharField(max_length=32,verbose_name='专业/职业',default='')
    class_num = models.DecimalField(max_digits=4,decimal_places=2,verbose_name='等级',default=1.0)
    mobile = models.CharField(max_length=14,verbose_name='手机号',null=True)
    email = models.EmailField(max_length=32,verbose_name='邮箱',null=True,unique=True)
    password = models.CharField(max_length=32, verbose_name='密码',null=False)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    login_time = models.DateTimeField(default='1970-01-01 00:00:00',verbose_name='登录时间')
    student_no = models.CharField(max_length=12,verbose_name='学号',default="unverified")
    portal_pass = models.CharField(max_length=32,verbose_name='门户密码',null=True)
    free_times = models.FloatField(verbose_name="免费次数",default=0.0)
    invitation_code = models.CharField(max_length=32,verbose_name="邀请码",null=True)
    is_blocked = models.BooleanField(verbose_name="是否黑名单",default=0)
    # upload_to是指定文件存储位置 MEIDIA_ROOT + upload_to的值
    # 即wiki/media/avatar
    avatar = models.ImageField(upload_to='avatar', default='', verbose_name='头像')


    class Meta:
        db_table = 'user_profile'
