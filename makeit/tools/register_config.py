from hashlib import md5
import base64
import time
import random




codes = 'QQJCTCPSMSHSCHZO'

class AccountInfo:
    def __init__(self):
        self.account_id = '8a216da873b8d5350173ba087a040082'
        self.token = 'ec4427f5a5134a50aa367f7cbf62cd89'
        self.app_id = '8a216da873b8d5350173ba087ae60088'
        self.main_url = 'https://app.cloopen.com:8883'
    #生成请求头
    def generate_headers(self):
        headers = {
            'Accept': 'Application/json',
            'Content-Type': 'application/json;charset=utf-8',
            'Content-Length': '70',
            'Authorization': ''
        }
        str_time = time.strftime('%Y%m%d%H%M%S')
        verif_str = self.account_id + ':' + str_time
        auth = base64.b64encode(verif_str.encode())
        headers['Authorization'] = auth.decode()
        return headers
    def generate_code(self):
        sixbit = ''
        for i in range(6):
            sixbit += str(random.randint(0,9))
        return sixbit
    #生成post请求中的data
    def generate_data(self,phone_number):
        code = self.generate_code()
        return {"to":str(phone_number),
                "appId":self.app_id,
                "templateId":"1",
                "datas":[code,"10"]}
    #生成url地址中查询字符串的SigParamater以及请求地址
    def generate_url(self):
        sig_string = self.account_id + self.token + time.strftime('%Y%m%d%H%M%S')
        hash_string = md5()
        hash_string.update(sig_string.encode())
        sigparamater = hash_string.hexdigest().upper()
        url = self.main_url + '/2013-12-26/Accounts/{accountSid}/SMS/TemplateSMS?sig={SigParameter}'.format(accountSid=self.account_id,SigParameter=sigparamater)
        return url

if __name__ == "__main__":
    a = AccountInfo()
    print(a.generate_headers())
    print(a.generate_url())
    print(a.generate_data(15140654692))