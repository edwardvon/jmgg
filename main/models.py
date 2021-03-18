from uuid import uuid4
from django.db import models

# Create your models here.
AREAS = (('szq', '市直'),
         ('pjq', '蓬江区'),
         ('jhq', '江海区'),
         ('xhq', '新会区'),
         ('tss', '台山市'),
         ('kps', '开平市'),
         ('eps', '恩平市'),
         ('hss', '鹤山市'))


class Requestments(models.Model):
    rid = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(verbose_name="名称", max_length=128, default="")
    project_code = models.CharField(verbose_name="项目编号", max_length=32, default="", null=True)
    price = models.FloatField(verbose_name="项目预算", null=True)
    deadline = models.DateTimeField(verbose_name="投标截止日期", null=True)
    agent = models.CharField(verbose_name="招标代理机构", max_length=32, null=True, default="")
    client = models.CharField(verbose_name="采购人", max_length=32, null=True, default="")
    area = models.CharField(verbose_name="市/区", max_length=16, null=True, default="", choices=AREAS)
    url = models.URLField(verbose_name="原网站链接", null=True, blank=True)
    pdf = models.CharField(verbose_name="招标文件链接", null=True, blank=True, default=None)
    pubdate = models.DateTimeField(verbose_name="发布时间", null=True)

    join_time = models.DateTimeField(auto_now=True)
    last_update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        def __str__(self):
            return self.name


class Tags(models.Model):
    tagid = models.CharField(unique=True, default=uuid4)
    tag = models.CharField(max_length=32, default="")
    num = models.IntegerField(default=0)


class Tagmap(models.Model):
    tagid = models.CharField(max_length=64, default="")
    rid = models.CharField(max_length=64, default="")


class Relationship(models.Model):
    rid = models.CharField(max_length=32, default="")
    nid = models.CharField(max_length=32, default="")
    type = models.CharField(max_length=8, default="")
