from django.conf.urls import url
from django.shortcuts import render, HttpResponse, redirect
from django.db.models.fields.related import ManyToManyField,ForeignKey,OneToOneField
from django.utils.safestring import mark_safe
from django.urls import reverse
from django import forms
from my_admin.utils.mypage import MyPage
from django.db.models import Q
import copy


class Showlist(object):
    """
    展示类：只服务于listview视图函数
    """

    def __init__(self, config_obj, data_list, request):
        self.config_obj = config_obj
        self.data_list = data_list
        self.request = request
        # 分页
        current_page = request.GET.get("page", 1)  # 获取当前页面
        all_data_amount = self.data_list.count()  # 获取当前模型表中的总数据量
        self.myPage_obj = MyPage(current_page, all_data_amount, request)  # 实例化对象
        self.current_show_data = data_list[self.myPage_obj.start:self.myPage_obj.end]

    # 获取一个新式actions格式：[{"text":"xxx","name":"patch_delete"},]
    def get_new_actions(self):
        add_actions = []
        add_actions.extend(self.config_obj.actions)
        add_actions.append(self.config_obj.patch_delete)

        new_actions = []    # 新式actions
        for func in add_actions:
            new_actions.append({
                "text":func.short_description,
                "name":func.__name__,
            })
        return new_actions

    # 获取一个新式list_filter格式:{"publish":[xx,xx,],"authors":[xx,xx,]}
    def get_new_list_filter(self):
        new_list_filter = {}
        for str_field in self.config_obj.list_filter:
            get_url_params = copy.deepcopy(self.request.GET)
            current_field_pk = get_url_params.get(str_field,0)
            field_obj = self.config_obj.model._meta.get_field(str_field)
            # 新建存放表中数据的列表
            model_list = []
            if current_field_pk == 0:
                a_tag = '<a style="color:purple" href="?{}">{}</a>'.format(get_url_params.urlencode(), "全部")
            else:
                get_url_params.pop(str_field)
                a_tag = '<a style="color:purple" href="?{}">{}</a>'.format(get_url_params.urlencode(), "全部")
            model_list.append(a_tag)
            # 判断是否是关联字段
            if isinstance(field_obj,ManyToManyField) or isinstance(field_obj,ForeignKey) or isinstance(field_obj,OneToOneField):
                rel_model = field_obj.rel.to
                rel_model_queryset = rel_model.objects.all()
                for rel_model_obj in rel_model_queryset:
                    get_url_params[str_field] = rel_model_obj.pk
                    if rel_model_obj.pk == int(current_field_pk):
                        a_tag = '<a class="active" href="?{}">{}</a>'.format(get_url_params.urlencode(), rel_model_obj)
                    else:
                        a_tag = '<a href="?{}">{}</a>'.format(get_url_params.urlencode(), rel_model_obj)
                    model_list.append(a_tag)
            else:
                current_model_queryset = self.config_obj.model.objects.values(str_field)
                for current_model_dict in current_model_queryset:
                    get_url_params[str_field] = current_model_dict[str_field]
                    if current_model_dict[str_field] == current_field_pk:
                        a_tag = '<a class="active" href="?{}">{}</a>'.format(get_url_params.urlencode(), current_model_dict[str_field])
                    else:
                        a_tag = '<a href="?{}">{}</a>'.format(get_url_params.urlencode(),current_model_dict[str_field])
                    model_list.append(a_tag)
            new_list_filter[str_field] = model_list
        return new_list_filter

    def get_header(self):
        # 创建数据表格头部分
        header_list = []
        for field_or_func in self.config_obj.get_new_list_display():
            # 判断 field_or_func 是否可以被调用
            if callable(field_or_func):
                add_header = field_or_func(self.config_obj, is_header=True)
            else:
                # 判断 field_or_func 是否为"__str__"
                if field_or_func == "__str__":
                    # 继承默认配置类，就默认展示当前访问模型表的表名
                    add_header = self.config_obj.model._meta.model_name.upper()
                else:
                    # 自定制配置类，就获取字段对象
                    field_obj = self.config_obj.model._meta.get_field(field_or_func)
                    add_header = field_obj.verbose_name
            header_list.append(add_header)

        return header_list

    def get_body(self):
        # 创建数据表格体部分
        new_data_list = []
        for data_obj in self.current_show_data:
            inner_data_list = []
            for field_or_func in self.config_obj.get_new_list_display():
                # 判断 field_or_func 是否可以被调用
                if callable(field_or_func):
                    field_value = field_or_func(self.config_obj, data_obj=data_obj)
                else:
                    # 针对继承默认配置类的模型表的list_display的值是"__str__".进行异常处理
                    try:
                        # 判断field_or_func 所对应的字段对象的类型是否为ManyToManyField
                        field_obj = self.config_obj.model._meta.get_field(field_or_func)
                        if isinstance(field_obj, ManyToManyField):
                            # 多对多关系的字段需要调用all()
                            rel_obj_list = getattr(data_obj, field_or_func).all()
                            rel_data_list = [str(item) for item in rel_obj_list]
                            field_value = ",".join(rel_data_list)
                        else:
                            # 除了多对多关系以外的字段都可以直接添加，无需调用all()
                            field_value = getattr(data_obj, field_or_func)
                            if field_or_func in self.config_obj.list_display_links:
                                # 若在当前访问模型表的配置类对象的list_display_links中能找到此field_or_func，则给此field_or_func对应的字段值添加a标签，可以跳转到编辑页面,再将构建好的a标签赋值给field_value
                                change_url = self.config_obj.get_change_url(data_obj)
                                field_value = mark_safe('<a href="{}">{}</a>'.format(change_url, field_value))

                    except Exception as e:
                        # field_or_func 为"__str__"
                        field_value = getattr(data_obj, field_or_func)
                inner_data_list.append(field_value)
            new_data_list.append(inner_data_list)

        return new_data_list


class ModelMyAdmin():
    model_form_class = []
    list_display = ["__str__", ]
    list_display_links = []
    search_fields = []
    actions = []
    list_filter = []

    def __init__(self, model):
        self.model = model
        self.model_name = self.model._meta.model_name
        self.app_label = self.model._meta.app_label

    # 批量删除函数
    def patch_delete(self,queryset):
        queryset.delete()
    # 定义汉语描述
    patch_delete.short_description = "批量删除"


    # 获取增删改查的url
    def get_list_url(self):
        list_url = "{}_{}_list".format(self.app_label, self.model_name)
        return reverse(list_url)

    def get_add_url(self):
        list_url = "{}_{}_add".format(self.app_label, self.model_name)
        return reverse(list_url)

    def get_delete_url(self, data_obj):
        list_url = "{}_{}_delete".format(self.app_label, self.model_name)
        return reverse(list_url, args=(data_obj.pk,))

    def get_change_url(self, data_obj):
        list_url = "{}_{}_change".format(self.app_label, self.model_name)
        return reverse(list_url, args=(data_obj.pk,))


    # 默认操作函数
    def delete(self, data_obj=None, is_header=False):
        if is_header:
            return "操作"
        else:
            return mark_safe('<a href="{}">删除</a>'.format(self.get_delete_url(data_obj)))

    def change(self, data_obj=None, is_header=False):
        if is_header:
            return "操作"
        else:
            return mark_safe('<a href="{}">编辑</a>'.format(self.get_change_url(data_obj)))

    def checkbox(self, data_obj=None, is_header=False):
        if is_header:
            return "选择"
        else:
            return mark_safe('<input type="checkbox" name="pk_list" value={}>'.format(data_obj.pk))


    # 获取新的list_display
    def get_new_list_display(self):
        new_list_display = []
        new_list_display.extend(self.list_display)
        new_list_display.insert(0, ModelMyAdmin.checkbox)
        new_list_display.append(ModelMyAdmin.delete)
        if not self.list_display_links:
            # 若继承默认配置类的list_display_links，则需要默认添加编辑列
            new_list_display.append(ModelMyAdmin.change)
        return new_list_display



    # 获取默认配置类或者自定制配置类中的model_form
    def get_model_form(self):
        if self.model_form_class:
            return self.model_form_class
        else:
            class ModelFormClass(forms.ModelForm):
                class Meta:
                    model = self.model
                    fields = '__all__'

            return ModelFormClass

    # 获取新的model_form(添加pop功能)
    def get_new_model_form(self,form):
        from django.forms.models import ModelChoiceField
        for bfield in form:
            if isinstance(bfield.field, ModelChoiceField):
                bfield.is_pop = True
                # 获取字段的字符串格式
                str_field = bfield.name
                # 获取关联字段所对应的表(类)
                rel_model = self.model._meta.get_field(str_field).rel.to
                # 获取关联字段所对应的表名
                str_model_name = rel_model._meta.model_name
                # 获取关联字段所对应的app名
                str_app_label = rel_model._meta.app_label
                # 通过反射获取到url
                _url = reverse("{}_{}_add".format(str_app_label,str_model_name))
                bfield.url = _url
                bfield.pop_back_id = "id_" + str_field
        return form



    # 获取定位搜索条件
    def get_search_condition(self, request):
        # 从url上获取填入的搜索值，没有就默认为空
        search_value = request.GET.get("query", "")
        # 实例化出一个搜索对象
        search_condition = Q()
        if search_value:
            # 将搜索联合条件更改为或，默认为且
            search_condition.connector = "or"
            for field in self.search_fields:
                search_condition.children.append((field + '__icontains', search_value))
        # 若不走if条件，则返回的是空搜索条件，即会显示所有信息
        return search_condition

    # 获取筛选搜索条件
    def get_filter_condition(self,request):
        filter_condition = Q()
        for key,val in request.GET.items():
            if key in ["page","query"]:
                continue
            filter_condition.children.append((key,val))
        return filter_condition

    # 视图函数（增删改查）
    def listview(self, request):
        if request.method == "POST":
            func_name = request.POST.get("actions","")
            pk_list = request.POST.getlist("pk_list")
            print("actions-->",func_name) #  food: --> patch_init
            print("pk_list-->",pk_list) # pk_list--> ['5061', '5062', '5063']
            queryset = self.model.objects.filter(pk__in = pk_list)
            if func_name:
                # func_name-->str 故需要通过反射来找到函数名
                action = getattr(self,func_name)
                # 执行函数
                action(queryset)

        # 获取添加数据的url
        add_url = self.get_add_url()
        # 获取展示数据的url
        list_url = self.get_list_url()

        # 获取当前模型表的所有数据
        data_list = self.model.objects.all()

        # 获取定位搜索条件对象
        search_condition = self.get_search_condition(request)
        # 获取筛选搜索条件对象
        filter_condition = self.get_filter_condition(request)
        # 数据过滤
        data_list = data_list.filter(search_condition).filter(filter_condition)
        # data_list = data_list.filter(search_condition)
        # 需求：要用到Showlist类中的两个方法，故需要先实例化对象
        show_list = Showlist(self, data_list, request)
        # 调用类中的方法或属性
        header_list = show_list.get_header()
        current_show_data = show_list.get_body()
        page_html = show_list.myPage_obj.ret_html()
        new_actions = show_list.get_new_actions()

        new_list_filter = show_list.get_new_list_filter()

        return render(request, "my-admin/listview.html", {
            "current_show_data": current_show_data,
            "header_list": header_list,
            "current_model": self.model_name,
            "add_url": add_url,
            "page_html": page_html,
            "search_fields": self.search_fields,
            "new_actions": new_actions,
            "list_filter":self.list_filter,
            "list_url":list_url,
            "new_list_filter":new_list_filter,
        })

    def addview(self, request):
        ModelFormClass = self.get_model_form()
        if request.method == "POST":
            form = ModelFormClass(request.POST)
            form_obj = self.get_new_model_form(form)
            if form_obj.is_valid():
                obj = form_obj.save()
                pop = request.GET.get("pop","")
                if pop:
                    form_data = str(obj)
                    pk = obj.pk
                    return render(request,"my-admin/pop.html",{"form_data":form_data,"pk":pk})
                else:
                    list_url = self.get_list_url()
                    return redirect(list_url)
            return render(request, "my-admin/addview.html", {
                "form_obj": form_obj,
                "model_name": self.model_name,
            })

        form = ModelFormClass()
        form_obj = self.get_new_model_form(form)

        return render(request, "my-admin/addview.html", {
            "form_obj": form_obj,
            "model_name": self.model_name,
        })

    def changeview(self, request, id):
        ModelFormClass = self.get_model_form()
        change_obj = self.model.objects.get(pk=id)
        if request.method == "POST":
            form = ModelFormClass(data=request.POST, instance=change_obj)
            form_obj = self.get_new_model_form(form)
            if form_obj.is_valid():
                form_obj.save()
                list_url = self.get_list_url()
                return redirect(list_url)
            return render(request, "my-admin/changeview.html", {
                "form_obj": form_obj,
                "model_name": self.model_name,
            })

        form = ModelFormClass(instance=change_obj)
        form_obj = self.get_new_model_form(form)
        return render(request, "my-admin/changeview.html", {
            "form_obj": form_obj,
            "model_name": self.model_name,
        })

    def deleteview(self, request, id):
        delete_obj = self.model.objects.get(pk=id)
        list_url = self.get_list_url()

        if request.method == "POST":
            delete_obj.delete()
            return redirect(list_url)

        form_obj = self.get_model_form()(instance=delete_obj)
        return render(request, "my-admin/delete.html", {
            "model_name": self.model_name,
            "form_obj": form_obj,
            "list_url": list_url,
        })

    def get_urls_02(self):
        res = [
            url(r'^$', self.listview, name="{}_{}_list".format(self.app_label, self.model_name)),
            url(r'^add/$', self.addview, name="{}_{}_add".format(self.app_label, self.model_name)),
            url(r'^(\d+)/change/$', self.changeview, name="{}_{}_change".format(self.app_label, self.model_name)),
            url(r'^(\d+)/delete/$', self.deleteview, name="{}_{}_delete".format(self.app_label, self.model_name)),
        ]
        return res

    @property
    def urls(self):
        return self.get_urls_02(), None, None


class MyAdminSite():
    def __init__(self):
        self._registry = {}

    def register(self, model, my_admin_class=None):
        if not my_admin_class:
            my_admin_class = ModelMyAdmin
        self._registry[model] = my_admin_class(model)

    def get_urls_01(self):
        res = []
        for model, config_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            add_url = url(r'^{}/{}/'.format(app_label, model_name), config_obj.urls)
            res.append(add_url)
        return res

    @property
    def urls(self):
        return self.get_urls_01(), None, None


site = MyAdminSite()
