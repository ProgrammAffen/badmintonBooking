from django.conf.urls import url
from . import views

urlpatterns = [
    # 测试app
    url(r'test',views.test),
    # 处理添加订单
    url(r'order_generation',views.generate_order),
    # 查看剩余名额
    url(r'rest_amount',views.check_rest_amount),
    # 查看订单
    url(r'get_orders',views.get_orders),
    # 取消订单
    url(r'delete_order',views.delete_order),
    # 查看备用订单
    url(r'check_backup',views.check_backup),
    # 锁定预备场地
    url(r'get_backup',views.get_backup),
]