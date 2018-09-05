from django.db import models


# 创建一张Teacher表
class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    tname = models.CharField(max_length=32,null=False)
    sex = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.tname


# 创建一张Course表
class Course(models.Model):
    id = models.AutoField(primary_key=True)
    cname = models.CharField(max_length=32,null=False)
    teacher = models.ForeignKey(to='Teacher',on_delete=models.CASCADE)

    def __str__(self):
        return self.cname


# 创建一张Student表
class Student(models.Model):
    id = models.AutoField(primary_key=True)
    sname = models.CharField(max_length=32,null=False)
    age = models.IntegerField(null=False)
    courses = models.ManyToManyField(to='Course')

    def __str__(self):
        return self.sname


