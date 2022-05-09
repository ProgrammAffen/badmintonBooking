from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from django.conf import settings
import time

#测试celery
@shared_task
def task_test():
    print("begin")
    for i in range(5):
        print(i)
    print("end")
    return "hello world"

# 发送验证邮件
@shared_task
def verfiy_reg_send_email(email_address,content):
    from_email = settings.DEFAULT_FROM_EMAIL
    sending = [email_address,]
    # content = '请15分钟内前往该地址进行验证' + '<h4>' + content + '</h4>'
    msg = EmailMultiAlternatives('松鼠树洞',content,from_email,sending)
    msg.content_subtype = 'html'
    msg.send()
    return {'code':200}