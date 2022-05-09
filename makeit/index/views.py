import json
import jwt
import time
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "."))
from django.http import JsonResponse
from django.shortcuts import render
from user.models import UserProfile
import time
from tools.check_login import check_log_status
# Create your views here.

#处理用户登录首页验证是否登录
@check_log_status
def index(request):
    if request.method == 'POST':
        email = request.user.email
        return JsonResponse({'code':200,'data':'Logged in'})