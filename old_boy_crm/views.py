from django.shortcuts import render, HttpResponse, redirect
from old_boy_crm import models
from my_admin.utils.mypage import MyPage
from django.http import JsonResponse


def change_record(request, id):
    if request.is_ajax():
        record = request.POST.get("record")
        models.StudentStudyRecord.objects.filter(pk=id).update(record=record)
        return HttpResponse("ok")


def record_score(request, id):
    # 查询录入成绩的该班级学习记录对象
    class_study_record_obj = models.ClassStudyRecord.objects.filter(pk=id).first()
    # 查询该班级学习记录所对应的所有学生学习记录
    student_study_record_queryset = class_study_record_obj.studentstudyrecord_set.all()
    '''
    # AJAX技术发送POST请求 版本1：前端写了两个ajax，无法确定到底是哪个ajax传来的请求，就没法更新数据 # 
    ===》会报错：django.db.utils.IntegrityError: NOT NULL constraint failed: old_boy_crm_studentstudyrecord.score
        if request.is_ajax():
            score = request.POST.get("score")
            homework_note = request.POST.get("homework_note")
            models.StudentStudyRecord.objects.filter(pk=id).update(score=score)
            models.StudentStudyRecord.objects.filter(pk=id).update(homework_note=homework_note)    
    '''

    '''
    # AJAX技术发送POST请求 版本2：将action作为数据传到后端，但是都用一个id，就会造成更新数据错乱 # 
    ===》录入班级学习记录pk=1的，更新数据无论更新哪个学生学习记录的id都会更新到学生学习记录的id=1中
        if request.is_ajax():
            action = request.POST.get("action")
            score = request.POST.get("score")
            homework_note = request.POST.get("homework_note")
            if action == "score":
                models.StudentStudyRecord.objects.filter(pk=id).update(score=score)
            else:
                models.StudentStudyRecord.objects.filter(pk=id).update(homework_note=homework_note)   
    '''

    '''
    # AJAX技术发送POST请求 版本3：将action和sid作为数据传到后端,成功更新到数据库中 # 
        if request.is_ajax():
            action = request.POST.get("action")
            sid = request.POST.get("sid")
            print("sid-->",sid)
            score = request.POST.get("score")
            homework_note = request.POST.get("homework_note")
            if action == "score":
                models.StudentStudyRecord.objects.filter(pk=sid).update(score=score)
            else:
                models.StudentStudyRecord.objects.filter(pk=sid).update(homework_note=homework_note) 
    '''

    '''
    # AJAX技术发送POST请求 版本4：使代码更简洁 # 
    ===》**{action:val}相当于 score=80 或者 homework_note = “继续努力！”
        if request.is_ajax():
            action = request.POST.get("action")
            sid = request.POST.get("sid")
            val = request.POST.get("val")
            models.StudentStudyRecord.objects.filter(pk=sid).update(**{action:val})
    '''
    # AJAX发送post请求 #
    if request.is_ajax():
        action = request.POST.get("action")
        sid = request.POST.get("sid")
        val = request.POST.get("val")
        models.StudentStudyRecord.objects.filter(pk=sid).update(**{action: val})

    '''
    # form表单发送POST请求 #
     request.POST--> <QueryDict: {'csrfmiddlewaretoken': ['napR4oJa8xIEKsKaIOEjTrYVL704sTA0HW7w8a8Eu4PPI6qVqGTwqgXlGDxIwtng'], 'score': ['0', '80'], 'homework_note': ['基础知识不扎实！', '继续努力！']}>
     在前端将name设置成：score_{{student_study_record_obj.pk}}、homework_note_{{student_study_record_obj.pk}}
     在后端获取到name和name对应的value：score_1:80           ==》 score 1   80 
                                homework_note_1:"继续努力"  ==》 homework_note 1 "继续努力"
    ===》根据需求：根据**{key:value}创建一个新的数据结构
    {
        1：{
            score：80，
            homework_note："继续努力"
        }，
        2：{
            score：60，
            homework_note："基础知识不扎实"
        }，
    }
    '''
    if request.method == "POST":
        new_dict = {}
        # 获取前端发送过来的数据
        for key, value in request.POST.items():
            if key == "csrfmiddlewaretoken":
                continue
            else:
                name, sid = key.rsplit("_", 1)
                # 利用不在的思想来创建内部嵌套的字典
                if sid not in new_dict:
                    # 若键不在新建的字典中，则添加此键和所对应的值（内部嵌套的字典）
                    new_dict[sid] = {name: value}
                else:
                    # 若键在新建的字典中，则直接在内部嵌套的字典中添加键值对
                    new_dict[sid][name] = value

        # 将新创建的字典遍历
        for sid, inner_dict in new_dict.items():
            models.StudentStudyRecord.objects.filter(pk=sid).update(**inner_dict)
        return redirect(request.path_info)

    # 分页
    current_page = request.GET.get("page", 1)  # 获取当前页面
    all_data_amount = student_study_record_queryset.count()  # 获取当前模型表中的总数据量
    myPage_obj = MyPage(current_page, all_data_amount, request)  # 实例化对象
    page_html = myPage_obj.ret_html()
    current_show_data = student_study_record_queryset[myPage_obj.start:myPage_obj.end]
    return render(request, "record_score.html", {
        "class_study_record_obj": class_study_record_obj,
        "student_study_record_queryset": student_study_record_queryset,
        "page_html": page_html,
        "current_show_data": current_show_data,
    })


def student_info(request, id):
    # 查询该学生对象
    student_obj = models.Student.objects.filter(pk=id).first()
    # 查询该学生对象所对应的所有班级信息
    rel_class_queryset = student_obj.class_list.all()

    if request.is_ajax():
        '''
        要返回给前端的数据结构如下：
        [
            ['day1', 80],
            ['day2', 55],
            ['day3', 70],
            ['day4', 66.78],
            ['day5', 86.06],
        ],
        '''
        # 获取该学生关联的班级id值
        cid = request.GET.get("cid")
        # 获取该学生所关联的班级下的所有的学生学习记录
        studentstudyrecord_list = models.StudentStudyRecord.objects.filter(student=id,classstudyrecord__class_obj=cid)
        ret_data = [["day{}".format(studentstudyrecord.classstudyrecord.day_num),studentstudyrecord.score] for studentstudyrecord in studentstudyrecord_list ]
        print(">>>",ret_data)   # [['day1', 40], ['day2', 80], ['day3', 80]]
        return JsonResponse(ret_data,safe=False)

    return render(request, "student_info.html", {
        "student_obj": student_obj,
        "rel_class_queryset": rel_class_queryset,
    })
