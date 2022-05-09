from django.shortcuts import render
from django.http import JsonResponse
import json
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "."))
import datetime
import time
from .models import OrderProfile,BackUpOrder
import redis
from user.models import UserProfile
from hashlib import md5
from django.db.models import Q
import selenium
from selenium import webdriver
from .tasks import send_QRcode,lock_order
from selenium.webdriver.chrome.options import Options
# Create your views here.

r = redis.Redis(host='127.0.0.1',port=6379,db=2,password='Aa136549.',decode_responses=True)

def test(request):
    return JsonResponse({"data":"hello"})

# 添加订单
def generate_order(request):
    if request.method == 'POST':
        json_str = request.body
        json_obj = json.loads(json_str)
        courts_list = json_obj["courts"]
        email = json_obj["email"]
        print(email)
        sports_type = json_obj["sportstype"]
        today_date = json_obj["today_date"]
        book_weekday = json_obj["book_weekday"]
        if courts_list == [] or email == "" or sports_type == "" or today_date == "" or book_weekday == "":
            return JsonResponse({'code':10402,'Error':'Unknown error'})
        # 验证当天名额是否已满 验证是否有免费次数 看是否重复预订场地 场地是否被预订
        booking_date = datetime.datetime.strptime(today_date,"%Y-%m-%d") + datetime.timedelta(2)
        courts = OrderProfile.objects.filter(booking_date=booking_date)
        id_list = []
        # TODO 如果列表中id个数大于等于10则不予预订，在此可以修改数量
        for order in courts:
            if order.user_id not in id_list:
                id_list.append(order.user_id)
        if len(id_list) >= 10:
            return JsonResponse({"code":10405,'Error':'The amount is full'})
        # 检查预定的场地是否被人预订
        orders = OrderProfile.objects.filter(booking_date=booking_date)
        booked_fields = []
        for order in orders:
            order = order.order_coordinate.strip('&').split('&')
            for single in order:
                booked_fields.append(single)
        print(booked_fields)
        for item in courts_list:
            if item in booked_fields:
                return JsonResponse({'code':10408,'Error':'Your wanted fields have been booked'})
        # 检查订单中是否有你的订单，如果再想订只能订相同场地的，并且写入不同订单中
        user = UserProfile.objects.filter(email=email)
        if user != []:
            user_id = user[0].id
            orders = OrderProfile.objects.select_related("user_id").filter(user_id=user_id,booking_date=booking_date)
            print(len(orders))
            if len(orders) != 0:
                field_type = orders[0].sports_type
                if field_type != sports_type:
                    return JsonResponse({'code': 10409, 'Error': 'You can not book other fields'})
                court_coordinate = orders[0].order_coordinate
                checked_court = court_coordinate.strip("&").split('&')[0].split('-')[0]
                for i in courts_list:
                    if i.split('-')[0] != checked_court:
                        return JsonResponse({'code':10409,'Error':'You can not book other fields'})
        # 查看用户是否有免费次数，如果有自动抵扣一次，如果没有计算应付金额
        user = UserProfile.objects.filter(email=email)
        if user:
            free_times = user[0].free_times
            if free_times >= 1:
                free_times -= 1
                UserProfile.objects.filter(email=email).update(free_times=free_times)
                is_use_free = 1
                total_money = 0
            else:
                is_use_free = 0
                # 预定时间为周末
                if int(book_weekday) == 6 or int(book_weekday) == 0:
                    if sports_type == "badminton":
                        if int(courts_list[0].split('-')[0]) < 5:
                            total_money = 0
                            for i in courts_list:
                                if int(i.split('-')[1]) < 10:
                                    total_money += 1
                                if int(i.split('-')[1]) >= 10:
                                    total_money += 2
                        else:
                            total_money = 0
                            for i in courts_list:
                                if int(i.split('-')[1]) < 10:
                                    total_money += 2
                                if int(i.split('-')[1]) >= 10:
                                    total_money += 3
                    elif sports_type == "basketball":
                        if int(courts_list[0].split('-')[0]) == 1 or int(courts_list[0].split('-')[0]) == 2:
                            total_money = 2.5 * len(courts_list)
                        else:
                            total_money = 5 * len(courts_list)
                    else:
                        return JsonResponse({'code':10407,'Error':'NO such sports type'})
                # 预订时间为工作日
                else:
                    if sports_type == "badminton":
                        if int(courts_list[0].split('-')[0]) < 5:
                            total_money = 0
                            for i in courts_list:
                                if int(i.split('-')[1]) < 4:
                                    total_money += 1
                                if int(i.split('-')[1]) >= 4:
                                    total_money += 2
                        else:
                            total_money = 0
                            for i in courts_list:
                                if int(i.split('-')[1]) < 4:
                                    total_money += 2
                                if int(i.split('-')[1]) >= 4:
                                    total_money += 3
                    elif sports_type == "basketball":
                        if int(courts_list[0].split('-')[0]) == 1 or int(courts_list[0].split('-')[0]) == 2:
                            total_money = 2.5 * len(courts_list)
                        else:
                            total_money = 5 * len(courts_list)
                    else:
                        return JsonResponse({'code':10407,'Error':'NO such sports type'})
        else:
            return JsonResponse({'code':10406,'Error':'Please register'})

        court_no = courts_list[0].split("-")[0]
        # 再次判断抢的场地是否有重合
        for item in courts_list[1:]:
            if item.split("-")[0] != court_no:
                return JsonResponse({'code':10403,'Error':'You can not choose different fields in the same time interval'})
        if UserProfile.objects.filter(email=email):
            user = UserProfile.objects.get(email=email)
            # 查看用户是否认证
            if user.student_no == "unverified":
                return JsonResponse({'code':10404,'Error':'Please go to student verification process'})
            else:
                user_id = user.id
                print(user_id)
        # 获取当前时间为订单时间加两天
        t = time.time() + 8 * 60 *60
        curr_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(t))
        # 抢场地的时间为当前时间
        booking_date = datetime.datetime.strptime(today_date,"%Y-%m-%d") + datetime.timedelta(2)
        # 将时间字符串与邮箱组合生成订单号
        order_no = curr_time + email
        hash = md5()
        hash.update(order_no.encode())
        order_no = hash.hexdigest()
        # 不着急生成时间，先将坐标以字符串形式存入，到时取出时再进行解析
        fields_str = ""
        for item in courts_list:
            fields_str += item
            fields_str += '&'
        order = OrderProfile()
        order.order_no = order_no
        order.sports_type = sports_type
        order.order_date = curr_time
        order.booking_date = booking_date
        order.booking_weekday = int(book_weekday)
        order.order_coordinate = fields_str
        order.is_use_free = is_use_free
        order.payment = total_money
        order.user_id = user
        order.user_id.save()
        order.save()
        # 再将订单号存入redis一个小时，以便删除订单时使用
        r.set(order_no,email,60 * 60)
        return JsonResponse({'code':200,"data":'Data generating succeeded'})
    else:
        return JsonResponse({'code':10401,'Error':'Post is required'})

# 查看剩余名额
def check_rest_amount(request):
    if request.method == 'GET':
        method = request.GET.get("method")
        today = request.GET.get("today")
        print(today)
        if method and today:
            if method == "rest_amount":
                booking_date = datetime.datetime.strptime(today, "%Y-%m-%d") + datetime.timedelta(2)
                courts = OrderProfile.objects.filter(booking_date=booking_date)
                court_id_list = []
                if courts != []:
                    for order in courts:
                        court_id = order.order_coordinate.strip('&').split("&")
                        for id in court_id:
                            court_id_list.append(id)
                id_list = []
                # TODO 如果列表中id个数大于等于10则不予预订，在此可以修改数量
                for order in courts:
                    if order.user_id not in id_list:
                        id_list.append(order.user_id)
                print(len(id_list))
                if len(id_list) >= 10:
                    return JsonResponse({"code": 200, 'rest_amount': 0})
                else:
                    print(10 - len(id_list))
                    return JsonResponse({'code':200,'data':{'rest_amount': 10 - len(id_list),"booked_fields":court_id_list}})
    else:
        return JsonResponse({'code':10410,'Error':'Get is required'})

# 查看订单
def get_orders(request):
    if request.method == "GET":
        email = request.GET.get("email")
        if not email:
            return JsonResponse({'code':10450,"data":'Please login'})
        user = UserProfile.objects.filter(email=email)
        if user:
            orders = OrderProfile.objects.select_related("user_id").filter(user_id=user[0].id)
            order_list = []
            if orders:
                for order in orders:
                    order_dict = {}
                    order_dict["order_no"]=order.order_no
                    order_dict["order_weekday"]=order.booking_weekday
                    order_dict["order_coordinate"]=order.order_coordinate
                    order_dict["sports_type"] = order.sports_type
                    order_dict["payment"] = order.payment
                    order_dict["order_date"] = order.order_date
                    order_dict["booking_date"] = order.booking_date
                    order_dict["order_status"] = order.order_status
                    order_list.append(order_dict)
                return JsonResponse({'code':200,'order_list':order_list})
            else:
                return JsonResponse({'code':200,"order_list":[]})
    else:
        return JsonResponse({'code':10411,'Error':'Get is required'})

#删除订单
def delete_order(request):
    if request.method == "POST":
        json_str = request.body
        json_obj = json.loads(json_str)
        email = json_obj["email"]
        order_no = json_obj["order_no"]
        if email == "" or order_no == "":
            return JsonResponse({'code':10413,'Error':'Unkown error'})
        if r.get(order_no):
            verif_email = r.get(order_no)
            if verif_email == email:
                order = OrderProfile.objects.filter(order_no=order_no)
                if order:
                    if order[0].is_use_free == 1:
                        user = UserProfile.objects.filter(email=email)
                        user.update(free_times=user[0].free_times + 1)
                    order.delete()
                    return JsonResponse({"code":200,'data':'Deletion succeeded'})
                else: return JsonResponse({'code':10701,'Error':'No such order'})
            else:
                return JsonResponse({'code':'10413','Error':'Wrong deletion of order'})
        else:
            return JsonResponse({'code':10414,"Error":'Deletion expired you can not delete the order'})
    else:
        return JsonResponse({'code':10412,'Error':'Post is required'})

# 查看备用订单
def check_backup(request):
    if request.method == "GET":
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        today_str = today.strftime("%Y-%m-%d")
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        unused_order = BackUpOrder.objects.filter(booking_date=tomorrow_str,compensate_to=None)
        backup = []
        for order in unused_order:
            backup.append([order.booking_date,order.order_coordinate,order.id])
        return JsonResponse({'code':200,'data':backup})
    else:
        return JsonResponse({'code':10415,'Error':'Get is required'})

# 锁定预备场地
def get_backup(request):
    if request.method == 'POST':
        json_str = request.body
        json_obj = json.loads(json_str)
        if json_obj == "" or json_obj == None:
            return JsonResponse({'code':10417,'Error':'Please login'})
        if json_obj["action"] == "lock_court":
            print(json_obj)
            email = json_obj["email"]
            court_no = int(json_obj["court_no"].split('-')[1])
            user_id = UserProfile.objects.filter(email=email)[0].id
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            order = OrderProfile.objects.filter(user_id=user_id,booking_date=tomorrow.strftime("%Y-%m-%d"))
            if not order:
                return JsonResponse({'code':10417,'Error':'You have not booked the court'})
            else:
                if order[0].order_status == "failed":
                    backup_order = BackUpOrder.objects.filter(id=court_no)
                    if backup_order[0].compensate_to == None:
                        backup_order.update(compensate_to=user_id)
                        order.update(order_status="compensated")
                        # TODO 新添加部分
                        payment = backup_order[0].backup_user_payment
                        court = backup_order[0].order_coordinate
                        lock_order(email,payment,court)
                        return JsonResponse({'code':200,'data':backup_order[0].order_coordinate})
                    else:
                        return JsonResponse({'code':10419,'Error':'We are sorry to announce the court is occupied'})
                else:
                    return JsonResponse({'code':10418,'Error':'You have already got a field'})
        elif json_obj["action"] == "get_QR":
            email = json_obj["email"]
            today = datetime.date.today().strftime("%Y-%m-%d")
            user = UserProfile.objects.filter(email=email)
            if user:
                user_id = user[0].id
                backup_order = BackUpOrder.objects.filter(compensate_to=user_id,booking_date=today)
                # print(backup_order[0])
                if backup_order:
                    booking_time = int(backup_order[0].order_coordinate.split(" ")[1].split(':')[0])
                    if (time.localtime().tm_hour >= booking_time - 1 and time.localtime().tm_min > 55) or time.localtime().tm_hour >= booking_time:
                        # TODO 截图
                        try:
                            student_no = backup_order[0].backup_user
                            portal_pass = backup_order[0].backup_portal_pass
                            chrome_options = Options()
                            chrome_options.add_argument('--headless')
                            chrome_options.add_argument('--disable-gpu')
                            browser = webdriver.Chrome(chrome_options=chrome_options)
                            browser.get("https://tycg.dlut.edu.cn/DLUT/html/DLUT_center/pages/changdi.html")
                            browser.set_window_size(500, 1200)
                            username = browser.find_element_by_xpath('//*[@id="un"]')
                            password = browser.find_element_by_xpath('//*[@id="pd"]')
                            username.send_keys(student_no)
                            password.send_keys(portal_pass)
                            login = browser.find_element_by_xpath('//*[@id="index_login_btn"]/input')
                            login.click()
                            self_center = browser.find_element_by_xpath('//*[@id="menu-3"]')
                            self_center.click()
                            my_court = browser.find_element_by_xpath('//*[@id="changdi"]')
                            my_court.click()
                            time.sleep(3)
                            # TODO 新添加部分
                            try:
                                court = browser.find_element_by_xpath('//*[@id="changdiTicket"]/div[2]')
                                court.click()
                            except Exception as e:
                                # print(e)
                                court = browser.find_element_by_xpath('//*[@id="changdiTicket"]/div[1]')
                                court.click()
                            time.sleep(0.2)
                            browser.get_screenshot_as_file('/home/maoqi/myproject/makeit/sportsbooking/QR_codes/{}-screenshot.png'.format(str(student_no)))
                            browser.close()
                            send_QRcode(email,student_no)
                            return JsonResponse({'code':200,'data':'The QR code is sent'})
                        except Exception as e:
                            print(e)
                            return JsonResponse({'code':10423,'Error':'Please get the QR code in valid time'})
                    else:
                        return JsonResponse({'code':10422,'Error':'The QR code is 5 min before starting available'})
                else:
                    return JsonResponse({'code':10421,'Error':'No order'})
            else:
                return JsonResponse({'code':10420,'Error':'Please login'})
    else:
        return JsonResponse({"code":10416,'Error':'Post is required'})