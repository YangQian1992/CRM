from django.db import models


# 创建用户表(User)
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    # 与角色表(Role)建立多对多关系
    roles = models.ManyToManyField(to="Role")

    def __str__(self):
        return self.username


# 创建角色表(Role)
class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    # 与权限表(Permission)建立多对多关系
    permissions = models.ManyToManyField(to="Permission")

    def __str__(self):
        return self.name


# 创建权限表(Permission)
class Permission(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=128)
    title = models.CharField(max_length=32)
    code = models.CharField(max_length=32,default=list)

    def __str__(self):
        return self.title
