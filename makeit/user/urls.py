from django.conf.urls import url
from . import views

#处理用户注册请求
urlpatterns = [
    # url(r'^mobile_registration',views.mobile_register),
    # 处理用户登陆请求
    url(r'^user_login',views.user_login),
    # 测试celery
    url(r'^celery',views.test_celery),
    # 处理用户注册请求
    url(r'^email_registration',views.email_register),
    # 处理用户邮件验证请求
    url(r'^email_verification',views.verify_email),
    # 处理用户邮箱登陆请求
    url(r'^email_login',views.email_login),
    # 检查ajax发送的账户查看请求
    url(r'check_status',views.check_login_status),
    # 处理用户认证学生身份请求
    url(r'student_verification',views.certificate_student),
    # 处理用户修改密码请求
    url(r'^info_alteration',views.alter_info),
]