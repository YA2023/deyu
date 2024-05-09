from django.utils.deprecation import MiddlewareMixin
from index_app.models import TUser
from django.http import HttpResponseForbidden#如果要反爬虫返回一个HttpResponseForbidden
# from django.http import HttpResponse
 #中间件随时随地执行,所以可以用来反爬虫,也可用来从cookie里读username实现七天免登录
# from django.shortcuts import redirect
class Auto_Login_MiddleWare(MiddlewareMixin):

    def process_request(self,request):

        username = request.COOKIES.get(
            "username")  # 取cookie  现cookies里只有username  如果能从cookies里取出username,说明之前有登录成功的人,这个cookies的存活时长是一周
        user = TUser.objects.filter(username=username)
        if user:
            request.session['username'] = user[0].username
            request.session['is_login'] = True
            print("中间件七天免登录用户", user[0].username)

        # print(request.META["REMOTE_ADDR"])  # META里的REMOTE_ADDR是访问用户的ip地址
        # # 一个反爬虫思路:给这个ip地址的用户加一个cookie,这个cookie的生命周期只有1分钟,之后每访问一次就给cookie值加1,一分钟内加到100就不能访问了,这就是初级反爬虫思路
        # if request.META["REMOTE_ADDR"] == "10.13.6.52":  # 这是写死了的
        #     print("王金阳来啦")
        #     request.status_code = 403
        #     return HttpResponseForbidden("滚")




        fanpachong_time = request.COOKIES.get("fanpachong_time")  # 尝试取出反爬虫时间fanpachong_time
        if fanpachong_time:
            fanpachong_time=int(fanpachong_time)
        # print("处理前cookie:",request.COOKIES)
        # print("fanpachong_time",fanpachong_time)

        # if fanpachong_time:  # 如果有反爬虫时间cookie,就说明他在60s内又发了一次请求.给cookie加1
        #     fanpachong_time = int(fanpachong_time) + 1
            # 然后这个cookie重新赋值
            # request.COOKIES.update("fanpachong_time", fanpachong_time, max_age=60 )  # 反爬虫cookie存活时间60s
            # request.COOKIES["fanpachong_time"] = fanpachong_time
            # 如果没有此cookie,说明他60s内未访问,这次访问了,给他加上
            #request里没有set_cookie 要去response


            # request.COOKIES["fanpachong_time"]=1
            # print("处理后cookie:",request.COOKIES)
            # request.session['fanpachong_time'] = fanpachong_time

        if fanpachong_time == 100:  #
            print("访问太快")
            request.status_code = 403
            return HttpResponseForbidden("滚")

        # 最后的最后,无返回值





    def process_response(self, request,response):
        fanpachong_time = request.COOKIES.get("fanpachong_time")
        # print(fanpachong_time)
        if fanpachong_time:
            fanpachong_time = int(fanpachong_time) + 1
            response.set_cookie("fanpachong_time", fanpachong_time,max_age=60)
            return response
        else:
            response.set_cookie("fanpachong_time", 1, max_age=60) #必须有两次请求间隔60s,否则不让访问
            # print("处理后cookie:", request.COOKIES)
            return response
        


