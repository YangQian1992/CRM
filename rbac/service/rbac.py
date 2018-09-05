from django.shortcuts import HttpResponse,render,redirect
# 导入中间件
from django.utils.deprecation import MiddlewareMixin
import re


# 权限中间件
class PermissionMiddleware(MiddlewareMixin):
    def process_request(self,request):
        current_path = request.path
        print("current_path-->",current_path)

        # 白名单
        white_url = ["/login/","/index/","/pcgetcaptcha/","/admin/",]
        for reg in white_url:
            ret = re.search(reg,current_path)
            if ret:
                # 如果匹配到白名单中的url,就直接放行
                return None

        # 校验用户是否登录
        user = request.session.get("username")
        if not user:
            # 如果没有登录认证，先跳转到登录页面
            return redirect("/login/")

        # 权限认证
        permission_list = request.session.get("permission_list")
        print("permission_list-->",permission_list)
        for reg in permission_list:
            # 解决正则匹配问题：xiaoxue只有查看的权限，但是没有加$,就会将编辑、删除的权限也有了
            reg = "^{}$".format(reg)
            ret = re.search(reg,current_path)
            if ret:
                return None
        return HttpResponse("无权限访问！")
