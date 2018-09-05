from django.shortcuts import HttpResponse,render,redirect
from django.http import JsonResponse
from utils.geetest import GeetestLib
from rbac import models
from app_school.forms import Login_Form


# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"

# 滑动验证码
def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)

# 登录认证
def login(request):
    res = {"code": 0}
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 滑动验证码校验通过
            username = request.POST.get('username')
            password = request.POST.get('password')
            # 从数据库中查找数据
            user = models.User.objects.filter(username=username,password=password).first()
            if user:
                # 用户名和密码正确,存储登录状态
                request.session["username"] = user.username
                # 查询当前登录用户的所有权限url
                permissions_queryset = user.roles.all().values("permissions__url","permissions__code","permissions__title").distinct()

                # 存储当前登录用户所有权限的列表
                permission_list = []
                # 存储当前登录用户所有菜单权限的列表
                permission_menu_list = []

                for permissions_dict in permissions_queryset:
                    permission_list.append(permissions_dict["permissions__url"])
                    # 判断permissions_dict是否含有list值
                    if permissions_dict["permissions__code"] == "list":
                        permission_menu_list.append({
                            "url":permissions_dict["permissions__url"],
                            "title":permissions_dict["permissions__title"],
                        })

                # 将权限列表存储到session中
                request.session["permission_list"] = permission_list
                # 将菜单权限列表存储到session中
                request.session["permission_menu_list"] = permission_menu_list
            else:
                # 用户名或者密码不正确
                res["code"] = 1
                res["msg"] = "用户名或者密码不正确！"
        else:
            # 滑动验证码校验失败
            res["code"] = 2
            res["msg"] = "验证码错误！"
        return JsonResponse(res)
    form_obj = Login_Form()
    return render(request, 'login_ajax_huadong.html', {"form_obj": form_obj})

# 主页面
def index(request):
    return render(request,"index.html")