from my_admin.service.sites import ModelMyAdmin, site
from old_boy_crm.models import *
from django.utils.safestring import mark_safe
from django.conf.urls import url
from old_boy_crm import views


site.register(Department)
site.register(UserInfo)
site.register(Course)
site.register(School)


class ClassListConfig(ModelMyAdmin):
    list_display = ["course", "semester", "teachers", "tutor"]


site.register(ClassList, ClassListConfig)


class CustomerConfig(ModelMyAdmin):
    # 自定制函数列--> 需求：将性别一列显示<男、女、保密>
    def display_gender(self, data_obj=None, is_header=False):
        if is_header:
            return "性别"
        else:
            return data_obj.get_gender_display()

    # 自定制函数列--> 需求：将咨询课程一列的数据显示一个一个的a标签
    def display_course(self, data_obj=None, is_header=False):
        if is_header:
            return "咨询课程"
        else:
            link_list = []
            for course_obj in data_obj.course.all():
                course = course_obj.name
                a_course = '<a href="/my_admin/old_boy_crm/course/">{}</a>'.format(course)
                link_list.append(a_course)
            return mark_safe(",".join(link_list))

    list_display = ["name", "consultant", display_gender, display_course, ]


site.register(Customer, CustomerConfig)

site.register(ConsultRecord)


class StudentConfig(ModelMyAdmin):
    def extra_url(self):
        res = []
        add_url = url(r'^(\d+)/student_info/$',views.student_info)
        res.append(add_url)
        return res

    def display_student_info(self,data_obj = None,is_header = False):
        if is_header:
            return "详细信息"
        else:
            a_student_info = '<a href="/my_admin/old_boy_crm/student/{}/student_info">查看详细信息</a>'.format(data_obj.pk)
            return mark_safe(a_student_info)

    list_display = ["customer","class_list",display_student_info]


site.register(Student,StudentConfig)


class ClassStudyRecordConfig(ModelMyAdmin):
    # 自定制函数列 --> 需求：添加一列查看详情信息，每条记录都是a标签，可以跳转到相对应的班级学习记录详情页
    def display_info(self, data_obj=None, is_header=False):
        if is_header:
            return "详情信息"
        else:
            a_class_study_record_info = '<a href="/my_admin/old_boy_crm/studentstudyrecord/?classstudyrecord={}">查看详情</a>'.format(
                data_obj.pk)
            return mark_safe(a_class_study_record_info)

    # 自定制函数列--> 需求：添加一列录入成绩，每条记录都是a标签，可以跳转到每条班级学习记录所对应的所有学生的录入成绩页面
    def handle_score(self,data_obj = None,is_header = False):
        if is_header:
            return "操作"
        else:
            a_record_score = '<a href="/my_admin/old_boy_crm/classstudyrecord/{}/record_score/">录入成绩</a>'.format(data_obj.pk)
            return mark_safe(a_record_score)

    # 重写extra_url方法
    def extra_url(self):
        res = []
        add_url = url(r'^(\d+)/record_score/$',views.record_score)
        res.append(add_url)
        return res

    list_display = ["class_obj", "day_num", "teacher", "homework_title", display_info,handle_score]

    # 批量初始化班级学习记录关联的学生学习记录
    def patch_init(self, request, queryset):
        for class_study_obj in queryset:
            # 查询出此班级学习记录对象对应的班级所关联的所有学生
            class_list_queryset = class_study_obj.class_obj  # 查找出选中的班级学习记录所对应的班级所有信息
            student_list_queryset = class_list_queryset.student_set.all()  # 通过多对多字段ORM操作（多对多&反向查询--> 关联表名_set）查找出此班级所对应的所有学生
            # 遍历所有学生对象，一一创建学生学习记录
            add_student_study_record_list = []
            for student_obj in student_list_queryset:
                # 直接用create(student=xxx,classstudyrecord=xxx)会很耗CPU，并且耗时，故需要通过bulk_create()语法来创建
                add_student_study_record = StudentStudyRecord(student=student_obj,
                                                              classstudyrecord=class_study_obj)  # 先给学生学习记录表添加数据，但是不会操作数据库
                add_student_study_record_list.append(add_student_study_record)
            StudentStudyRecord.objects.bulk_create(add_student_study_record_list)

    # 对批量初始化函数进行汉语描述
    patch_init.short_description = "批量初始化学生学习记录"
    # 将批量初始化函数添加到actions中
    actions = [patch_init, ]


site.register(ClassStudyRecord, ClassStudyRecordConfig)


class StudentStudyRecordConfig(ModelMyAdmin):
    def display_record(self, data_obj=None, is_header=False):
        if is_header:
            return "出勤"
        else:
            return data_obj.get_record_display()

    # 自定制函数列 --> 需求：将本节成绩一列显示<A+、A、B+>
    def display_score(self, data_obj=None, is_header=False):
        if is_header:
            return "本节成绩"
        else:
            return data_obj.get_score_display()

    '''
    修改出勤的第一种方式：批量修改出勤的函数   
    '''
    # 批量迟到
    def patch_late(self,request,queryset):
        queryset.update(record="late")
    patch_late.short_description = "迟到"
    # 批量已签到
    def patch_checked(self,request,queryset):
        queryset.update(record="checked")
    patch_checked.short_description = "已签到"
    actions = [patch_late,patch_checked]


    '''
   修改出勤的第二种方式：自定制函数列--> 需求：将每条记录写成select标签
    '''
    # 第一个发送请求的方式：AJAX发送post请求 #
    def display_select_record(self,data_obj = None,is_header = False):
        if is_header:
            return "上课记录"
        else:
            html = '<select class="record" pk="{}">'.format(data_obj.pk)
            for item in StudentStudyRecord.record_choices:
                if data_obj.record == item[0]:
                    add_option = '<option selected value={}>{}</option>'.format(item[0],item[1])
                else:
                    add_option = '<option value={}>{}</option>'.format(item[0], item[1])
                html += add_option
            html += '</select>'
            return mark_safe(html)
    # 重写父类extra_url方法
    def extra_url(self):
        res = []
        add_url = url(r'^(\d+)/change_record/$',views.change_record)
        res.append(add_url)
        return res

    list_display = ["student", "classstudyrecord", display_record, display_select_record, display_score]


site.register(StudentStudyRecord, StudentStudyRecordConfig)
