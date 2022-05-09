import requests
from lxml import etree
import execjs
import copy
import time
import datetime
import json
import random
from multiprocessing import Process
from selenium import webdriver


class GetInfo():
    def __init__(self,username,password):
        self.login_url = "https://sso.dlut.edu.cn/cas/login?service=https%3A%2F%2Ftycg.dlut.edu.cn%2Fdiantuo%2FpcLogin.do"
        self.get_second_url = "https://sso.dlut.edu.cn/cas/login;JSESSIONIDCAS={jic}?service=https%3A%2F%2Ftycg.dlut.edu.cn%2Fdiantuo%2FpcLogin.do"
        self.query_fileds_url = "https://tycg.dlut.edu.cn/diantuo/fieldSale/listFieldSale.do"
        self.username = username
        self.password = password
        self.first_key = "1"
        self.second_key = "2"
        self.third_key = "3"
        self.badminton_type = "9b28cdb90dbd11ea8ad0005056ad05e4"
        self.basketball_type = "611fd8290dc111ea8ad0005056ad05e4"
        self.volleyball_type = "a522b01e0dc111ea8ad0005056ad05e4"
        self.login_headers = {
            "authority": "sso.dlut.edu.cn",
            "method": "POST",
            "path": "/cas/login?service=https%3A%2F%2Fportal.dlut.edu.cn%2Ftp%2F",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,de-DE;q=0.8,de;q=0.7,en-US;q=0.6,en;q=0.5",
            "cache-control": "max-age=0",
            # "content-length": "332",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": "cas_hash=; Language=zh_CN; JSESSIONIDCAS={jic}",
            "origin": "https://sso.dlut.edu.cn",
            "referer": "https://tycg.dlut.edu.cn/",
            "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        self.sid = self.get_sid()["sid"]
        # 此函数用于登录时将sid发送至pclogin以及login服务器，及时写入信息防止登录过期
        # self.login_status = self.get_login()
        # self.login_status1 = self.get_login_check()#此函数用于加强校验，目前不需要，未来如果需要取消注释即可

    def get_first_LT_and_JSESSIONCAS(self):
        '''
        获取lt和jsessionidcas这两个参数
        :return:
        '''
        for i in range(50):
            try:
                res = requests.get(url=self.login_url,timeout=5)
                print("lt和jsessioncas:",res.status_code)
                if res.status_code == 200:
                    break
            except Exception as e:
                print(e)
                continue
        html_text = res.text
        html = etree.HTML(html_text, etree.HTMLParser())
        lt = html.xpath('//*[@id="lt"]/@value')[0]
        execution = html.xpath('//*[@name="execution"]/@value')[0]
        headers = res.headers
        jsessioncas = headers["Set-Cookie"].split(";")[2].split(",")[1].split("=")[1]
        return {"lt":lt,"JSESSIONCAS":jsessioncas,"execution":execution}

    def get_ticket_and_CASTGC(self):
        '''
        获取ticket和CASTGC这两个参数
        :return:
        '''
        infos = self.get_first_LT_and_JSESSIONCAS()
        lt = infos["lt"]
        execution = infos["execution"]
        jssesioncas = infos["JSESSIONCAS"]
        rsa = self.des_encipher_algorithm(lt)
        data = {
            "rsa": rsa,
            "ul": str(len(self.username)),
            "pl": str(len(self.password)),
            "lt": lt,
            "execution": execution,
            "_eventId": "submit"
        }
        headers = self.login_headers
        headers = copy.deepcopy(headers)
        cookie = headers["cookie"].format(jic=jssesioncas)
        headers["cookie"] = cookie
        formated_cookie = {}
        formated_cookie["cas_hash"] = ""
        formated_cookie["Language"] = "zh_CN"
        formated_cookie["JSESSIONIDCAS"] = jssesioncas
        headers["path"] = "/cas/login;JSESSIONIDCAS={jic}?service=https%3A%2F%2Ftycg.dlut.edu.cn%2Fdiantuo%2FpcLogin.do".format(jic=jssesioncas)
        headers["Referer"] = "https://sso.dlut.edu.cn/cas/login?service=https%3A%2F%2Ftycg.dlut.edu.cn%2Fdiantuo%2FpcLogin.do"
        for i in range(5):
            try:
                res = requests.post(url=self.get_second_url.format(jic=jssesioncas), headers=headers, data=data,cookies=formated_cookie,allow_redirects=False,timeout=random.randint(6,10))
                print("ticket和castgc:",res.status_code)
                if res.status_code == 302:
                    break
            except Exception as e:
                print(e)
                continue
        # print(res.text)
        cookie = requests.utils.dict_from_cookiejar(res.cookies)
        return {"url":res.headers["Location"],"CASTGC":cookie["CASTGC"],"JSESSIONCAS":infos["JSESSIONCAS"]}

    def des_encipher_algorithm(self,lt):
        '''
        此处为前端加密算法的使用，为des加密
        :param lt: lt为获取登录页面时隐藏在页面代码中的字符串
        :return: 加密后的数据
        '''
        data = self.username + self.password + lt
        encrypted_data = execjs.compile(open(r"./des_encode.js").read()).call("strEnc",data,self.first_key,self.second_key,self.third_key)
        return encrypted_data

    def get_sid(self):
        '''
        此函数用于获取sid，并且在实例化对象时就要获取，因为后续一些列操作都依赖于同一个sid
        :return:
        '''
        info = self.get_ticket_and_CASTGC()
        headers = {}
        headers["user-agent"] = self.login_headers["user-agent"]
        headers["referer"] = 'https://sso.dlut.edu.cn/'
        for i in range(50):
            try:
                r = requests.get(url=info["url"],headers=headers,allow_redirects=False,timeout=6)
                print("sid:",r.status_code)
                if r.status_code == 302:
                    break
            except Exception as e:
                print(e)
                continue
        # print(requests.utils.dict_from_cookiejar(r.cookies))
        print(requests.utils.dict_from_cookiejar(r.cookies))
        return requests.utils.dict_from_cookiejar(r.cookies)

    def get_login(self):
        '''
        此函数用于将最新sid写入服务器否则会提示401登录过期,不在体育馆开放期时无用，不能在实例化时就调用
        :return:
        '''
        headers = {}
        headers["user-agent"] = self.login_headers["user-agent"]
        headers["cookie"] = "sid=" + self.sid
        headers["referer"] = "https://sso.dlut.edu.cn/"
        headers["host"] = "tycg.dlut.edu.cn"
        cookies = {
            "sid":self.sid
        }
        for i in range(5):
            try:
                res_pclogin = requests.get(url="https://tycg.dlut.edu.cn/diantuo/pcLogin.do",headers=headers,cookies=cookies,allow_redirects=False,timeout=random.randint(4,7))
                print("res_pclogin:",res_pclogin.status_code)
                if res_pclogin.status_code == 302:
                    break
            except Exception as e:
                print(e)
                continue
        headers.pop("referer")
        for i in range(200):
            try:
                res_login = requests.get(url="http://tycg.dlut.edu.cn/diantuo/login.do",headers=headers,cookies=cookies,allow_redirects=False,timeout=random.randint(5,8))
                print("res_login:",res_login.status_code)
                print(res_login.text)
                if res_login.status_code == 302:
                    print("第" + str(i) + "次结束登陆操作" )
                    return 1
                else:
                    time.sleep(random.randint(1,3)*0.5)
            except Exception as e:
                print(e)
                continue
        print("未登陆成功")

    def get_login_check(self):
        headers = {
            "User-Agent":self.login_headers["user-agent"],
            "Cookie": "sid=" + self.sid,
            "Content-Type": "application/json",
            "Origin":"https://tycg.dlut.edu.cn",
            "Host":"tycg.dlut.edu.cn",
            "Referer":"https://tycg.dlut.edu.cn/pc_app/index.html",
        }
        cookies = {
            'sid':self.sid
        }
        url = "https://tycg.dlut.edu.cn/diantuo/loginCheck.do"
        res = requests.post(url=url,headers=headers,cookies=cookies,data=json.dumps({}))
        print(res.text)
        url1 = "https://tycg.dlut.edu.cn/diantuo/findMemberByMemberIdWithDllg_zcr.do"
        res1 = requests.post(url=url1,headers=headers,cookies=cookies,data=json.dumps({}))
        print(res1.text)
        headers["Referer"] = "https://tycg.dlut.edu.cn/pc_app/ticket_purchase.html"
        res2 = requests.post(url=url1,headers=headers,cookies=cookies,data=json.dumps({}))
        url2 = "https://tycg.dlut.edu.cn/diantuo/card/judgeThisCardType.do"
        res3 = requests.post(url=url2,headers=headers,cookies=cookies,data=json.dumps({}))
        url3 = "https://tycg.dlut.edu.cn/diantuo/listApiTicketSale.do"
        for i in range(2):
            res4 = requests.post(url=url3,headers=headers,cookies=cookies,data=json.dumps({"gamesNum":"","operator_role":"admin","orgId":"c4f67f3177d111e986f98cec4bb1848c","timeSolt":"","type":"pw","deliveryTerminal":"门户端"}))
        headers["Referer"] = "https://tycg.dlut.edu.cn/pc_app/site_reserve.html"
        res4 = requests.post(url=url, headers=headers, cookies=cookies, data=json.dumps({}))
        res5 = requests.post(url=url2,headers=headers,cookies=cookies,data=json.dumps({}))
        url4 = "https://tycg.dlut.edu.cn/diantuo/fieldSale/listApiFieldSaleNew1.do"
        today = datetime.date.today().strftime("%Y-%m-%d")
        print(today)
        week = ""
        if time.localtime().tm_wday == 0:
            week = "星期一"
        if time.localtime().tm_wday == 1:
            week = "星期二"
        if time.localtime().tm_wday == 2:
            week = "星期三"
        if time.localtime().tm_wday == 3:
            week = "星期四"
        if time.localtime().tm_wday == 4:
            week = "星期五"
        if time.localtime().tm_wday == 5:
            week = "星期六"
        if time.localtime().tm_wday == 6:
            week = "星期日"
        print(week)
        res5 = requests.post(url=url4,headers=headers,cookies=cookies,data=json.dumps({"fieldSaleStatus":1,"operator_role":"admin","orgId":"c4f67f3177d111e986f98cec4bb1848c","today":today,"week":week,"deliveryTerminal":"门户端"}))
        url5 = "https://tycg.dlut.edu.cn/diantuo/common/getServerDate.do"
        headers["Referer"] = "https://tycg.dlut.edu.cn/pc_app/site_reserve3.html"
        res6 = requests.post(url=url5,headers=headers,cookies=cookies)



    def get_rest_fields(self,field_type):
        '''
        #查询剩余场地，在预订时被占用时进行查询
        :param field_type:“basketball”或“badminton"
        :return:
        '''
        pay_load = {
            "fieldSaleId": "",
             "operator_role": "admin",
             "orgId": "c4f67f3177d111e986f98cec4bb1848c",
             "today": "",
             "week": ""
        }
        if field_type == "badminton":
            pay_load["fieldSaleId"] = self.badminton_type
        if field_type == "basketball":
            pay_load["fieldSaleId"] = self.basketball_type
        today = datetime.date.today() + datetime.timedelta(days=1)
        week = ""
        if time.localtime().tm_wday == 0:
            week = "星期二"
        if time.localtime().tm_wday == 1:
            week = "星期三"
        if time.localtime().tm_wday == 2:
            week = "星期四"
        if time.localtime().tm_wday == 3:
            week = "星期五"
        if time.localtime().tm_wday == 4:
            week = "星期六"
        if time.localtime().tm_wday == 5:
            week = "星期日"
        if time.localtime().tm_wday == 6:
            week = "星期一"
        pay_load["today"] = today.strftime("%Y-%m-%d")
        pay_load["week"] = week
        # 查询场地的日期均为当前日期的第二天
        headers = {}
        headers["user-agent"] = self.login_headers["user-agent"]
        headers["cookie"] = "sid=" + self.sid
        headers["referer"] = 'https://tycg.dlut.edu.cn/pc_app/site_reserve3.html'
        headers["content-type"] = "application/json"
        cookies = {
            "sid":self.sid
        }
        res = requests.post(url=self.query_fileds_url,headers=headers,data=json.dumps(pay_load),cookies=cookies)
        print(res.headers["Date"])
        fields_info = res.json()["data"]
        rest_fields = {}
        for data in fields_info:
            # print(data["place"])
            available_time = []
            i = 1
            for child_data in data["data"]:
                if child_data["status"] == 0:
                    # print(str(i) + ":" + child_data["time"])
                    available_time.append(str(i) + "=" + child_data["time"])
                    i += 1
                else:
                    i += 1
            rest_fields[data["place"]] = available_time
        return rest_fields

    def get_avail_fields(self,field_type):
        '''
        有些场地为教师专用，学生不可以预订，此函数用于查询可以预订的场次，利用当天的信息即可，被学生预订状态码为2，未预定是0
        :param field_type: “basketball” or “badminton”
        :return: 返回学生可以预订的场地以及场次
        '''
        pay_load = {
            "fieldSaleId": "",
            "operator_role": "admin",
            "orgId": "c4f67f3177d111e986f98cec4bb1848c",
            "today": "",
            "week": ""
        }
        if field_type == "badminton":
            pay_load["fieldSaleId"] = self.badminton_type
        if field_type == "basketball":
            pay_load["fieldSaleId"] = self.basketball_type
        today = datetime.date.today() + datetime.timedelta(days=1)
        today = today.strftime("%Y-%m-%d")
        week = ""
        if time.localtime().tm_wday == 0:
            week = "星期一"
        if time.localtime().tm_wday == 1:
            week = "星期二"
        if time.localtime().tm_wday == 2:
            week = "星期三"
        if time.localtime().tm_wday == 3:
            week = "星期四"
        if time.localtime().tm_wday == 4:
            week = "星期五"
        if time.localtime().tm_wday == 5:
            week = "星期六"
        if time.localtime().tm_wday == 6:
            week = "星期日"
        pay_load["week"] = week
        pay_load["today"] = today
        headers = {}
        headers["user-agent"] = self.login_headers["user-agent"]
        headers["cookie"] = "sid=" + self.sid
        headers["referer"] = 'https://tycg.dlut.edu.cn/pc_app/site_reserve3.html'
        headers["content-type"] = "application/json"
        cookies = {
            "sid": self.sid
        }
        res = requests.post(url=self.query_fileds_url, headers=headers, data=json.dumps(pay_load), cookies=cookies)
        fields_info = res.json()["data"]
        available_fields = {}
        for data in fields_info:
            # print(data["place"])
            available_time = []
            i = 1
            for child_data in data["data"]:
                # print(str(i)+ " : " + child_data["time"])
                available_time.append(str(i)+ "=" + child_data["time"])
                i += 1
            available_fields[data["place"]] = available_time
        return available_fields

    def generate_sign(self):
        '''
        生成订单时最重要的参数sign，需要从服务端获得
        :return:
        '''
        url = "https://tycg.dlut.edu.cn/diantuo/createSign.do"
        form_data = {
            "operator_role":"admin",
            "orgId":"c4f67f3177d111e986f98cec4bb1848c"
        }
        headers = {
            "User-Agent": self.login_headers["user-agent"],
            "Content-Type":"application/json",
            "Host": "tycg.dlut.edu.cn",
            "Origin": "https://tycg.dlut.edu.cn",
            "Referer": "https://tycg.dlut.edu.cn/pc_app/site_reserve2.html",
            "Cookie":"sid=" + self.sid,
            "Connection":"keep-alive",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors"
        }
        cookies = {
            "sid":self.sid
        }
        for i in range(200):
            try:
                res = requests.post(url=url,headers=headers,data=json.dumps(form_data),cookies=cookies,timeout=random.randint(8,12))
                if res.json()["sign"]:
                    if len(res.json()["sign"]) == 40:
                        print("sign是:",res.json()["sign"])
                        print("第" + str(i) + "次结束获取sign")
                        return res.json()["sign"]
                    else:
                        time.sleep(0.5 * random.randint(1,3))
            except Exception as e:
                print("错误为:",e)
                time.sleep(0.5 * random.randint(1, 3))
                continue
        print("未得到sign")

    def generate_order_list(self,sports_type,coordinate_y,field_place):
        '''

        :param sports_type:
        :param coordinate_y:
        :param field_place:羽毛球用int数字表示，篮球用字符串排球用数字1
        :return:
        '''
        if sports_type == "badminton":
            sports_code = self.badminton_type
            length = 120
            field_name = "羽毛球(学生)"
            x = field_place - 1
            if field_place in [1,2,3,4]:
                single_price = 8
            elif field_place in [5,6,7,8,9,10,11,12,14,15]:
                single_price = 16
            else:
                return {"Error":"Invalid Data"}
            place_no = str(field_place)
            place = place_no + "号场"
        elif sports_type == "basketball":
            if field_place == "1-半2":
                x = 0
            if field_place == "1-半1":
                x = 1
            if field_place == "2":
                x = 2
            sports_code = self.basketball_type
            length = 60
            field_name = "篮球(学生)"
            if field_place in ["1-半1","1-半2"]:
                single_price = 12
                place = field_place.split("-")[0] + "号场" + field_place.split("-")[1]
            elif field_place == "2":
                single_price = 20
                place = field_place + "号场"
            else:
                return {"Error": "Invalid Data"}
            place_no = str(field_place)
        elif sports_type == "VolleyBall":
            field_name = "排球馆(学生)"
            sports_code = self.volleyball_type
            length = 60
            place_no = str(field_place)
            place = place_no + "号场"
            single_price = 20
            x = 0
        else:
            return {"Error":"Wrong sports type"}
        if single_price == 8:
            money = str(single_price) + ".0"
        else:
            money = str(single_price) + ".00"
        total_price = single_price * len(coordinate_y)
        # 需要预订明天的场次
        str_date = datetime.date.today() + datetime.timedelta(days=1)
        str_date = str_date.strftime("%Y-%m-%d")
        order_list = []
        for y in coordinate_y:
            order_data = {
                "fieldSaleId": sports_code,
                "length": length,
                "money": money,
                "num": 1,
                "price": single_price,
                "status": 0,
                "step": int(length * 0.5),
                "time": "",  # str
                "place_no": place_no,
                "place": place,
                "date": str_date,
                "fieldName": field_name,
                "x": x,  # int
                "y": 0  # int
            }
            order_data["time"] = y[1]
            order_data["y"] = y[0]
            order_list.append(order_data)
        #print(order_list)
        return [order_list,total_price]

    def generate_order(self,sports_type,coordinate_y,field_place):
        list_info = self.generate_order_list(sports_type,coordinate_y,field_place)
        orderChildListTemp = list_info[0]
        if sports_type == "badminton":
            field_name = "羽毛球(学生)"
        if sports_type == "basketball":
            field_name = "篮球(学生)"
        if sports_type == "VolleyBall":
            field_name = "排球馆(学生)"
        total_price = list_info[1]
        str_date = datetime.date.today() + datetime.timedelta(days=1)
        str_date = str_date.strftime("%Y-%m-%d")
        str_total_price = str(total_price) + ".00"
        sign = self.generate_sign()
        payload = {
            "fieldName": field_name,
            "goodsParentType": "field定",
            "insurance": 0,
            "offMainSumPrice": str_total_price,
            "operator_role": "admin",
            "orderBackPrice": 0,
            "orderChildListTemp":orderChildListTemp,
            "orderMainId": "",
            "orderMainSumHaspay": str_total_price,
            "orderMainSumPrice": str_total_price,
            "orderMains": [],
            "orderReturnSourceObj": {},
            "orderServiceChildList": [],
            "orgId": "c4f67f3177d111e986f98cec4bb1848c",
            "payCode": "",
            "payType": "财务统一支付网关",
            "platform": "PCWEB",
            "printStatus": 1,
            "sign": sign,
            "today": str_date,
            "flreeCountFlag": False
        }
        #print(payload)
        headers = {
            "User-Agent": self.login_headers["user-agent"],
            "Cookie": "sid=" + self.sid,
            "Content-Type": "application/json",
            "Origin": "https://tycg.dlut.edu.cn",
            "Host": "tycg.dlut.edu.cn",
            "Referer": "https://tycg.dlut.edu.cn/pc_app/site_reserve2.html",
        }
        cookies = {
            'sid': self.sid
        }
        curr_time = time.time()
        url = "https://tycg.dlut.edu.cn/diantuo/addOrder.do?sign={sign}".format(sign=sign)
        for i in range(5):
            try:
                res = requests.post(url=url,headers=headers,cookies=cookies,data=json.dumps(payload),timeout=random.randint(2,4))
                # print(res.text)
                # if res:
                #     print(res.text)
                #     res_code = res.json()['code']
                #     print(res_code)
                #     if res_code == 200 or res_code == 400:
                #         print(res.json())
                #         print("第" + str(i) + "次结束完成订单")
                #         break
                #     elif res_code == 300:
                #         # 服务器错误
                #         print("busy:",res.status_code)
                #         time.sleep(1)
            except Exception as e:
                continue
        print("订单用时:",time.time() - curr_time)

    def look_up_order(self):
        '''
        查找未付款订单
        :return:
        '''
        url = 'https://tycg.dlut.edu.cn/diantuo/listApiOrderMain.do'
        headers = {
        "User-Agent": self.login_headers["user-agent"],
        "Content-Type":"application/json",
        "Host": "tycg.dlut.edu.cn",
        "Origin": "https://tycg.dlut.edu.cn",
        "Referer": "https://tycg.dlut.edu.cn/pc_app/my_order.html",
        "Cookie":"sid=" + self.sid,
        "Connection":"keep-alive",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors"
        }
        payload = {
            "ap_status": False,
            "ap_time": "时间",
            "deleteStatus": "1",
            "memberName_likeDouble": "",
             "operator_role": "admin",
            "orgId": "c4f67f3177d111e986f98cec4bb1848c",
            "orgIdCopy": "",
            "pageIndex": 0,
            "pageSize": 10,
            "payDate": [0, 1],
            "payStatus": "",
            "orderChildProductType": "",
            "payType": "",
            "total": 0,
            "productNameOrMainId": "",
            "createTime_smallEqualThanStr": "2021-03-15",
            "createTime_largerEqualThanStr": "2020-12-15",
            "sortname": "create_time",
            "sortorder": "desc"
        }
        cookies = {
            'sid': self.sid
        }
        str_date = datetime.date.today()
        str_date = str_date.strftime("%Y-%m-%d")
        payload["createTime_smallEqualThanStr"] = str_date
        payload["createTime_largerEqualThanStr"] = str_date
        try:
            res = requests.post(url=url,headers=headers,cookies=cookies,timeout=30,data=json.dumps(payload))
        except Exception as e:
            print('超时未获得订单')
        # print(res.json()['rows'])
        order_unpaid = []
        for i in res.json()['rows']:
            if i['orderMainPayStatus'] == '0':
                print(i['orderMainId'],i['createTime'])
                order_unpaid.append(i['orderMainId'])
        return order_unpaid

    def keep_order(self):
        url = 'https://tycg.dlut.edu.cn/diantuo/pay/dllgPay.do'
        headers = {
        "User-Agent": self.login_headers["user-agent"],
        "Content-Type":"application/json",
        "Host": "tycg.dlut.edu.cn",
        "Origin": "https://tycg.dlut.edu.cn",
        "Referer": "https://tycg.dlut.edu.cn/pc_app/jumpPayment.html",
        "Cookie":"sid=" + self.sid,
        "Connection":"keep-alive",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors"
        }
        cookies = {
            'sid': self.sid
        }
        payload = {
            "orderMainId":"",
            "returnUrl":"https://tycg.dlut.edu.cn/pc_app/return.html"
        }
        unpaid_order = self.look_up_order()
        for order in unpaid_order:
            for i in range(5):
                try:
                    payload["orderMainId"] = order
                    res = requests.post(url=url,headers=headers,data=json.dumps(payload),cookies=cookies,timeout=30)
                    if res:
                        break
                except Exception as e:
                    continue


if __name__ == "__main__":
    # ["21804139", "dj960702"]
    print("开始等待")
    while True:
        if time.localtime().tm_hour == 7 and time.localtime().tm_min == 0 and time.localtime().tm_sec == 0:
            time.sleep(0.5)
            break
    a = GetInfo("21904031","lyclsxlmw5471")
    b = GetInfo("21904096","Aa136549")
    c = GetInfo("31904173","rui1996??")
    d = GetInfo("21804131","xh2641127668")
    e = GetInfo("31804162","zlzl5216")
    # while True:
    #     if time.localtime().tm_hour == 7 and time.localtime().tm_min == 0 and time.localtime().tm_sec == 0:
    #         time.sleep(0.05)
    #         break
    a.get_login()
    b.get_login()
    c.get_login()
    d.get_login()
    e.get_login()
    p1 = Process(target=a.generate_order, args=("badminton",[[1,"15:00-16:00"],[2,"16:00-17:00"],],11))
    p2 = Process(target=b.generate_order, args=("badminton",[[3,"17:00-18:00"],[4,"18:00-19:00"],],11))
    p3 = Process(target=d.generate_order, args=("badminton",[[4,"19:00-20:00"],[5,"20:00-21:00"],],11))
    p4 = Process(target=b.generate_order, args=("badminton", [[1, "15:00-16:00"], [2, "16:00-17:00"], ], 12))
    p5 = Process(target=a.generate_order, args=("badminton", [[3, "17:00-18:00"], [4, "18:00-19:00"], ], 12))
    p6 = Process(target=c.generate_order, args=("badminton", [[4, "19:00-20:00"], [5, "20:00-21:00"], ], 12))
    p7 = Process(target=c.generate_order, args=("badminton", [[1, "15:00-16:00"], [2, "16:00-17:00"], ], 14))
    p8 = Process(target=d.generate_order, args=("badminton", [[3, "17:00-18:00"], [4, "18:00-19:00"], ], 14))
    p9 = Process(target=a.generate_order, args=("badminton", [[4, "19:00-20:00"], [5, "20:00-21:00"], ], 14))
    p10 = Process(target=d.generate_order, args=("badminton", [[1, "15:00-16:00"], [2, "16:00-17:00"], ], 15))
    p11 = Process(target=c.generate_order, args=("badminton", [[3, "17:00-18:00"], [4, "18:00-19:00"], ], 15))
    p12 = Process(target=b.generate_order, args=("badminton", [[4, "19:00-20:00"], [5, "20:00-21:00"], ], 15))
    p13 = Process(target=e.generate_order, args=("basketball",[[1,"15:00-15:30"],[2,"15:30-16:00"],[3,"16:00-16:30"],[4,"16:30-17:00"]],"1-半1"))
    p14 = Process(target=e.generate_order, args=("basketball",[[5,"17:00-17:30"],[6,"17:30-18:00"],[7,"18:00-18:30"],[8,"18:30-19:00"]],"1-半1"))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()
    p9.start()
    p10.start()
    p11.start()
    p12.start()
    p13.start()
    p14.start()
    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()
    p9.join()
    p10.join()
    p11.join()
    p12.join()
    p13.join()
    p14.join()

