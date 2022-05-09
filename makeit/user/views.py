import datetime
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "."))
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from .models import UserProfile
import hashlib
import requests
from tools import register_config
from tools.check_login import check_log_status
import time
import jwt
import re
import redis
from .tasks import task_test,verfiy_reg_send_email
from student_verify import StudentVerification


import html
# Create your views here.
#数据库0

def test_celery(request):
    html = task_test()
    return HttpResponse(html)

r = redis.Redis(host='127.0.0.1',port=6379,db=0,password='Aa136549.',decode_responses=True)
#处理用户注册相关：ajax处理用户手机号是否被注册，验证码，以及用户注册
def mobile_register(request):
    if request.method == 'POST':
        json_str = request.body
        json_obj = json.loads(json_str)
        #在传过来的数据中有用户名 代表手机号已通过验证
        if 'username' in json_obj:
            #存入数据库之前需要对传进来的数据进行再次检查
            token = json_obj.get('tokens').encode()
            username = json_obj.get('username')
            password = json_obj.get('password')
            pass_again = json_obj.get('password_again')
            veri_code = json_obj.get('code')
            mobile = json_obj.get('mobile')
            email = json_obj.get('email')
            if username == '' or password == '' or pass_again == '' or veri_code == '' or mobile == '' or type(token) != bytes:
                return JsonResponse({"code":10110,'Error':'Please check your filling in'})
            #检查用户名是否合规,只能包含下划线数字字母汉字，且数字不能开头，下划线不能开头结尾
            res1 = re.findall('\W+',username)
            res2 = re.findall(r'(^[0-9]|^_|_$)',username)
            if res1 or res2:
                return JsonResponse({'code':10106,'Error':'Username is invalid'})
            #检查验证码是否过期
            try:
                check_token = jwt.decode(json_obj['tokens'],'check_mobile','HS256')
            except Exception as e:
                print(e)
                return JsonResponse({'code':10104,'Error':'The verification code is out-dated'})
            #检验传过来的手机号和token中取出的手机号是否一致
            if mobile != check_token['number']:
                return JsonResponse({'code':10109,'Error':'Mobile phone error,please check again!'})
            #检查验证码是否正确,先从redis中取出手机号对应的验证码
            check_code = r.get(check_token['number'])
            if not check_code:
                #若取不到证明手机号不正确
                return JsonResponse({'code':10104,'Error':'The phone number is incorrect'})
            if check_code != veri_code:
                #若从发过来的数据中取出的验证码和redis中的不一致，证明手机号与验证码不匹配或者用户输错验证码
                return JsonResponse({'code':10108,'Error':'The verification code is incorrect'})
            if password != pass_again:
                return JsonResponse({'code':10107})
            #最好再检验一遍手机号是否存在
            phone = UserProfile.objects.filter(mobile=mobile)
            if phone:
                return JsonResponse({'code': 10102, 'Error': 'The number is already existed'})
            #检查无误后再存入数据库 此处不在前端做验证了
            else:
                user = UserProfile()
                user.email = json_obj.get('email')
                user.mobile = json_obj.get('mobile')
                user.username = json_obj.get('username')
                password = json_obj.get('password') + 'maomaoqi'
                #给密码加盐 并存入MySQL
                hash_pass = hashlib.md5()
                hash_pass.update(password.encode())
                hash_pass = hash_pass.hexdigest()
                user.password = hash_pass
                user.save()
                return JsonResponse({'code':200,'info':'Register succeeded'})
        else:
            # ajax处理手机号是否已被注册
            mobile = json_obj.get('mobile')
            print(mobile)
            if mobile:
                phone = UserProfile.objects.filter(mobile=mobile)
                if phone:
                    return JsonResponse({'code':10102,'Error':'The number is already existed'})
                else:
                    return JsonResponse({'code':200})
    #用户向后台请求验证码
    elif request.method == 'GET':
        number = request.GET.get('number')
        if int(number):
            # TODO 此处用celery 分布式任务发送短信验证码
            # 向容联云通讯申请短信
            url = register_config.AccountInfo().generate_url()
            headers = register_config.AccountInfo().generate_headers()
            datas = register_config.AccountInfo().generate_data(number)
            res = requests.post(url=url,data=json.dumps(datas),headers=headers).text
            print(res)
            if res:
                res = eval(res)
                if res['statusCode'] == "000000":
                    #设置token的过期时间，保证验证码的时效性
                    payload = {
                        'exp': time.time() + 600,
                        'number': number,
                    }
                    key = 'check_mobile'
                    token = jwt.encode(payload=payload,key=key,algorithm='HS256')
                    #将手机号以及验证码存入redis设置超时时间10分钟
                    code = datas['datas'][0]
                    r.set(number,code,1000 * 60 *10)
                    return JsonResponse({'code':200,'token':token.decode()})
                elif res['statusCode'] == "160038":
                    return JsonResponse({'code':10104,'Error':'You have sent request so frequently,please wait'})
                else:
                    return JsonResponse({'code':10103,'Error':'Fail to require verification code'})
        else:
            return JsonResponse({'code':10103,'Error':'Unknown error when send request to get verification code'})
    else:
        return JsonResponse({'code':10101,'Error':'"Post "or "get" is required'})

#处理用户登录请求
def user_login(request):
    if request.method == 'POST':
        json_str = request.body
        json_obj = json.loads(json_str)
        mobile = json_obj.get('mobile')
        password = json_obj.get('password')
        is_checked = json_obj.get('is_checked')
        if ' ' in mobile or ' ' in password or mobile == '' or password == '':
            return JsonResponse({'code':10202,'Error':'Please check your input'})

        # 此处按照原有规则给密码加盐
        check_pass = password + 'maomaoqi'
        check_hash = hashlib.md5()
        check_hash.update(check_pass.encode())
        check_hash = check_hash.hexdigest()
        if UserProfile.objects.filter(mobile=mobile):
            if UserProfile.objects.filter(password=check_hash):
                #到此处为用户名密码都正确，根据用户是否勾选免登陆设置token的过期时间
                if is_checked == True:
                    #勾选免登陆，保存用户名30天
                    exp_time = 60 * 60 * 24 * 30
                else:
                    #未勾选则保存用户名1天
                    exp_time = 60 * 60 *24
                username = UserProfile.objects.values('username').filter(mobile=mobile)[0]['username']
                print(username)
                curr_time = str(time.time())
                user = UserProfile.objects.get(mobile=mobile)
                user.login_time = time.strftime('%Y-%m-%d %H:%M:%S')
                user.save()
                payload = {'username':username,
                           'mobile':mobile,
                           'login_time':curr_time,
                           'exp': time.time() + exp_time
                           }
                key = 'check_status'
                token = jwt.encode(payload=payload,key=key,algorithm='HS256')
                print(token)
                return JsonResponse({'code':200,'username':username,'token':token.decode()})
            else:
                #此处为密码错误
                print('Password is invalid')
                return JsonResponse({'code':10203,'Error':'Username or password is invalid'})
        else:
            #此处为用户名不存在
            print('Username does not exist')
            return JsonResponse({'code':10203,'Error':'Username or password is invalid'})
    else:
        return JsonResponse({'code':10201,'Error':'A post request is required'})

# ****************************************************************************************************
# 此处开始为邮箱注册登陆等功能

#处理用户的邮箱注册请求并发送验证邮件
def email_register(request):
    if request.method == 'POST':
        #json数据从request.body中取到
        json_str = request.body
        json_obj = json.loads(json_str)
        try:
            username = json_obj["username"]
            email = json_obj["email"]
            password = json_obj["password"]
            password_repeat = json_obj["password_repeat"]
        except Exception as e:
            print(e)
            return JsonResponse({'code':10304,'Error':'Can not parse your information'})
        finally:
            res_username = re.findall('^(?!_)(?!.*?_$)[a-zA-Z0-9_\u4e00-\u9fa5]{4,10}$',username)
            res_email = re.findall('^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$',email)
            res_password = re.findall('^\w{6,16}$',password)
            if username == "" or password == "" or email == "":
                return JsonResponse({'code':10302,"Error":"Please check your input"})
            if not res_username or not res_email or not res_password:
                return JsonResponse({'code': 10302, "Error": "Please check your input"})
            if password != password_repeat:
                return JsonResponse({'code':10303,"Error":"The passwords are not equal"})
            # 检查邮箱是否被注册
            if UserProfile.objects.filter(email=email):
                return JsonResponse({'code':10305,'Error':'The email has already existed'})
            else:
                # 发送验证邮件，首先进行加密
                verif_code = register_config.AccountInfo().generate_code()
                key = 'reg_ver_email'
                exp_time = 15 * 60
                payload = {
                    'username':username,
                    'ver_code':verif_code,
                    'email':email,
                    'exp':time.time() + exp_time
                }
                password = str(password) + 'maomaoqi'
                # 给密码加盐 并加密，与验证码一起暂存至redis
                hash_pass = hashlib.md5()
                hash_pass.update(password.encode())
                hash_pass = hash_pass.hexdigest()
                token = jwt.encode(payload=payload,key=key,algorithm='HS256')
                r.set(username,verif_code + "+" + hash_pass,15 * 60 * 1000)
                # TODO 正式部署项目时需要修改地址
                deal_reg_ver_url = '请15分钟内前往该地址进行验证' + '<h4>' + 'http://127.0.0.1:5000/email_verification?username=' + token.decode() + '</h4>'
                # 使用celery给客户发送验证邮件，由同级的tasks.py导入
                verfiy_reg_send_email.delay(email,deal_reg_ver_url)
                return JsonResponse({'code':200,'data':'Verification email has sent'})
    else:
        return JsonResponse({'code':10301,"Error":"Post is required"})

# 处理用户的验证邮件
def verify_email(request):
    # 有两种情况，用户注册发送验证邮箱；用户忘记密码发送验证邮箱
    if request.method == 'GET':
        jwt_code = request.GET.get('username')
        print(jwt_code)
        if not jwt_code:
            return JsonResponse({'code':10307,'Error':'Please do register process again'})
        else:
            # token存在验证其是否过期
            try:
                decode_result = jwt.decode(jwt_code,key='reg_ver_email',algorithms='HS256')
            except Exception as e:
                print(e)
                return JsonResponse({'code':10308,'Error':'The login status is expired'})
            username = decode_result['username']
            verify_code = decode_result['ver_code']
            email = decode_result['email']
            if UserProfile.objects.filter(email=email):
                return JsonResponse({'code':10310,'Error':'You have successfully registered'})
            if r.get(username):
                ver_code = r.get(username).split("+")[0]
                password = r.get(username).split("+")[1]
                print(password)
                if ver_code != verify_code:
                    return JsonResponse({'code':10309,'Error':'The registration status is expired'})
                else:
                    log_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    user = UserProfile()
                    user.email = email
                    user.login_time = log_time
                    user.password = password
                    user.username = username
                    # user.free_times = 1
                    user.save()
                    exp_time = 60 * 60 * 24 * 7
                    payload = {
                        'username': username,
                        'email': email,
                        'exp': time.time() + exp_time,
                        'login_time':log_time
                    }
                    key = 'login_key'
                    token = jwt.encode(payload=payload,key=key,algorithm='HS256')
                    return JsonResponse({'code':200,'username':username,'email':email,'token':token.decode()})
            else:
                #取不到邮箱
                return JsonResponse({'code':10309,'Error':'The registration status is expired'})
    # 用户忘记密码进行验证重新生成密码
    elif request.method == 'POST':
        json_str = request.body
        request_type = json.loads(json_str)['request_type']
        print(request_type)
        if request_type == 'password_update':
            email = json.loads(json_str)['email']
            print(email)
            if email:
                if UserProfile.objects.filter(email=email):
                    send_email = UserProfile.objects.values('email').filter(email=email)[0]['email']
                    password = str(register_config.AccountInfo().generate_code()) + 'update_password'
                    hash_pass = hashlib.md5()
                    hash_pass.update(password.encode())
                    hash_pass = hash_pass.hexdigest()
                    send_pass = hash_pass[:7:1]
                    print(send_pass)
                    content = '您的新密码为：' + send_pass + ',请登陆后尽快修改'
                    verfiy_reg_send_email.delay(send_email,content)
                    # 将修改后的密码加盐在数据库中进行更新
                    save_pass = send_pass + 'maomaoqi'
                    hasing = hashlib.md5()
                    hasing.update(save_pass.encode())
                    save_pass = hasing.hexdigest()
                    UserProfile.objects.filter(email=email).update(password=save_pass)
                    return JsonResponse({'code':200,'Data':'Update completed'})
            else:
                # email为空
                return JsonResponse({'code':10315,'Error':'Please check your input'})
        else:
            return JsonResponse({'code':10314,'Error':'PLease check your input'})
    else:
        return JsonResponse({'code':10306,'Error':'Get or post is required'})


# 用户邮箱登陆
def email_login(request):
    if request.method == 'POST':
        json_str = request.body
        user_info = json.loads(json_str)
        try:
            email = user_info['email']
            password = user_info['password']
            if email == '' or password == '':
                return JsonResponse({'code':10331,'Error':'PLease check your input'})
        except Exception as e:
            print(e)
            return JsonResponse({'code':10312,'Error':'Please login again'})
        if not UserProfile.objects.filter(email=email):
            # 邮箱不存在,用户未注册
            return JsonResponse({'code':10313,'Error':'Please register'})
        else:
            # 邮箱存在,验证密码
            password = str(password) + 'maomaoqi'
            hash_pass = hashlib.md5()
            hash_pass.update(password.encode())
            hash_pass = hash_pass.hexdigest()
            print(hash_pass)
            db_pass = UserProfile.objects.values('password').filter(email=email)[0]['password']
            print(db_pass)
            username = UserProfile.objects.values('username').filter(email=email)[0]['username']
            if db_pass == hash_pass:
                log_time = time.strftime("%Y-%m-%d %H:%M:%S")
                UserProfile.objects.filter(email=email).update(login_time=log_time)
                exp_time = 60 * 60 * 24 * 7
                payload = {
                    'username': username,
                    'email': email,
                    'exp': time.time() + exp_time,
                    'login_time': log_time
                }
                key = 'login_key'
                token = jwt.encode(payload=payload, key=key, algorithm='HS256')
                return JsonResponse({'code':200,'username':username,'email':email,'token':token.decode()})
            else:
                return JsonResponse({'code':10312,'Error':'Please login'})
    else:
        return JsonResponse({'code':10311,'Error':'Post is required'})

#处理用户更改信息请求
def alter_info(request):
    if request.method == 'POST':
        json_str = request.body
        json_obj = json.loads(json_str)
        new_pass = json_obj["new_pass"]
        pass_repeat = json_obj["pass_repeat"]
        email = json_obj["email"]
        password = json_obj["password"]
        if email == "" or password == "":
            return JsonResponse({'code':10325,'Error':'Please check your input'})
        password += 'maomaoqi'
        print(password)
        hash_pass = hashlib.md5()
        hash_pass.update(password.encode())
        hash_pass = hash_pass.hexdigest()
        # 如果邮箱存在，继续验证
        if UserProfile.objects.filter(email=email):
            user = UserProfile.objects.get(email=email)
            # 如果用户名下的密码与传过来的元密码相等
            if user.password == hash_pass:
                # 对新密码进行校验
                res_password = re.findall('^\w{6,16}$', new_pass)
                print(res_password)
                print(new_pass)
                if res_password:
                    if new_pass == pass_repeat:
                        password = new_pass + 'maomaoqi'
                        hash_pass = hashlib.md5()
                        hash_pass.update(password.encode())
                        hash_pass = hash_pass.hexdigest()
                        user.password = hash_pass
                        user.save()
                        return JsonResponse({'code':200,'data':'Password changed'})
                    else:
                        JsonResponse({'code':10329,'Error':'The two passwords are not equal'})
                else:
                    return JsonResponse({'code':10328,'Error':'Please check your password setting'})
            else:
                return JsonResponse({'code':10326,'Error':'Password is invalid'})
        else:
            return JsonResponse({'code':10327,'Error':'Email does not exist'})
    else:
        return JsonResponse({'code':10324,'Error':'Post is required'})

# 处理用户信息认证请求
def certificate_student(request):
    if request.method == 'POST':
        json_str = request.body
        json_obj = json.loads(json_str)
        student_no = json_obj['student_no']
        student_pass = json_obj['ver_password']
        if student_no == '' or student_pass == '':
            return JsonResponse({'code':10330,'Error':'Please check your input'})
        email = json_obj['email']
        if not UserProfile.objects.filter(email=email):
            return JsonResponse({'code':10331,'Error':'Please register'})
        # 账户中存在该学号 查询是否为绑定的邮箱
        if UserProfile.objects.filter(student_no=student_no):
            user = UserProfile.objects.get(student_no=student_no)
            if user.email != email:
                return JsonResponse({'code':10323,'Error':'This Student number has already been recorded'})
        personal_data = StudentVerification(student_no,student_pass)
        personal_data.get_first_LT_and_JSESSIONCAS()
        try:
            res = personal_data.get_ticket_and_CASTGC()
        except Exception as e:
            print(e)
            return JsonResponse({'code':10322,'Error':'Authentication failed'})
        if res:
            if res['url'] and res['CASTGC'] and res['JSESSIONCAS']:
                user = UserProfile.objects.get(email=email)
                user.student_no = student_no
                user.portal_pass = student_pass
                user.save()
                return JsonResponse({'code':200,'data':'Verification succeeded'})
            else:
                return JsonResponse({'code': 10322, 'Error': 'Authentication failed'})
        else:
            return JsonResponse({'code': 10322, 'Error': 'Authentication failed'})
    else:
        return JsonResponse({'code':10321,'Error':'Post is required'})

# 处理登陆账户自动请求
@check_log_status
def check_login_status(request):
    user = request.user
    return JsonResponse({'code':200,'data':{'email':user.email,'student_no':user.student_no,'username':user.username,'free_times':user.free_times}})