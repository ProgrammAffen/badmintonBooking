'''
脚本功能：检查用户登录状态，即保持会话
当用户访问必须登录的资源，未登录则弹到登录页面
'''
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from django.http import JsonResponse
from user.models import UserProfile
import jwt
import json

def check_log_status(func):
    def wrapper(request,*args,**kwargs):
        json_str = request.body
        json_obj = json.loads(json_str)
        token = json_obj['Authorization']
        username = json_obj['username']
        # token不存在，根本没登录
        if not token:
            return JsonResponse({'code': 10316, 'Error': 'Please log in'})
        else:
            # 登录已过期
            try:
                result = jwt.decode(token, key='login_key', algorithms='HS256')
            except Exception as e:
                print('登录已过期')
                return JsonResponse({'code': 10317, 'Error': 'Please log in'})
            username_decode = result['username']
            email = result['email']
            login_time_token = result['login_time']
            print(login_time_token)
            # 传过来的用户名跟token解码出的用户名不一致
            if username != username_decode:
                return JsonResponse(
                    {'code': 10318, 'Error': 'Some problems with your login status,please log in again'})
            # 数据库中找不到用户
            if not UserProfile.objects.filter(email=email):
                return JsonResponse({'code': 10319, 'Error': 'User does not exists,please register'})
            login_time = UserProfile.objects.values('login_time').filter(email=email)[0]['login_time']
            timeArray = time.strptime(login_time_token,"%Y-%m-%d %H:%M:%S")
            # 此处表示用户在别处登录，记录下的登录时间比token中的登录时间晚
            if time.mktime(timeArray) < login_time.timestamp():
                return JsonResponse({'code': 10320, 'Error': 'User has logged in at other platform'})
            request.user = UserProfile.objects.get(email=email)
            return func(request,*args,**kwargs)
    return wrapper

def check_verified(func):
    def wrapper(request,*args,**kwargs):
        print(request.body)
        json_str = request.body
        json_obj = json.loads(json_str)
        email = json_obj["email"]
        if email == "":
            return JsonResponse({'code':10460,"Error":"Please login"})
        user = UserProfile.objects.filter(email=email)
        if user:
            print(user[0].student_no)
            if user[0].student_no == "unverified":
                return JsonResponse({'code': 10462, 'Error': 'PLease do student verification'})
            else:
                print(user[0].student_no)
                return func(request, *args, **kwargs)
        else:
            return JsonResponse({'code':'10601','Error':'PLease register'})
    return wrapper