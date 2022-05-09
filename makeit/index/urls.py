from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'check_log',views.index)
]