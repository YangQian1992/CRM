"""day89_CMS系统 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from my_admin.service.sites import site
from app_school import views


urlpatterns = [
    # 系统自带的admin组件
    url(r'^admin/', admin.site.urls),
    # 自定制的组件（可直接导入使用）
    url(r'^my_admin/', site.urls),
    # 滑动验证码版本的登录认证
    url(r'^pcgetcaptcha/$', views.pcgetcaptcha),
    url(r'^login/$',views.login),
    # 主页面
    url(r'^index/$',views.index),

]
