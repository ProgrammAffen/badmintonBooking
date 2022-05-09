from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from django.conf import settings

@shared_task
def send_QRcode(email_address,student_no):
    from_email = settings.DEFAULT_FROM_EMAIL
    sending = [email_address, ]
    msg = EmailMultiAlternatives('松鼠树洞', "<h3>请在5分钟内到体育馆进行验证哦</h3>", from_email, sending)
    msg.content_subtype = 'html'
    file_name = str(student_no) + "-screenshot.png"
    QR_directory = '/home/maoqi/myproject/makeit/sportsbooking/QR_codes/'
    msg.attach_file(QR_directory + file_name)
    msg.send()
    return {'code': 200}

@shared_task
def lock_order(email_address,pay_method,court,):
    from_email = settings.DEFAULT_FROM_EMAIL
    sending = [email_address, ]
    msg = EmailMultiAlternatives('松鼠树洞','<h3>已为你锁定候补场地:' + str(court) + '请在1小时内向此支付宝账号:'
                                 + pay_method + '支付场地原价,在场地时间开始5分钟前可申请二维码并于体育馆处进行核销</h3>',from_email,sending)
    msg.content_subtype = 'html'
    msg.send()
    return {'code':200}