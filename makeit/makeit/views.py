from django.http import HttpResponse

#测试跨域连接
def test(request):
    if request.method == 'GET':
        return HttpResponse('ok')

