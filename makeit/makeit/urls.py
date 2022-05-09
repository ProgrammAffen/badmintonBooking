"""makeit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #测试跨域
    url(r'^test/',views.test),
    #分部式路由用户部分
    url(r'^v1/user/',include('user.urls')),
    #处理用户首页部分
    url(r'^v1/index/',include('index.urls')),
    # 处理订场部分
    url(r'v1/sports_booking/',include('sportsbooking.urls')),
    #测试celery
    url(r'v1/user/celery/',include('user.urls'))
]
