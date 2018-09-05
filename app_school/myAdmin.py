from my_admin.service.sites import ModelMyAdmin,site
from app_school.models import Teacher,Course,Student


class TeacherConfig(ModelMyAdmin):
    search_fields = ["tname"]
    list_display = ["tname","sex"]


site.register(Teacher,TeacherConfig)


class CourseConfig(ModelMyAdmin):
    list_filter = ["teacher"]


site.register(Course,CourseConfig)


class StudentConfig(ModelMyAdmin):
    list_display = ["sname","age"]
    list_display_links = ["sname","age"]
    list_filter = ["courses"]


site.register(Student,StudentConfig)
