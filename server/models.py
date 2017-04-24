# coding:utf-8
from django.db import models


class Compute(models.Model):
    name = models.CharField(max_length=20,verbose_name=u'服务器名称')
    hostname = models.CharField(max_length=20,verbose_name=u'服务器IP地址')
    login = models.CharField(max_length=20,verbose_name=u'用户名（用于SSH链接）')
    password = models.CharField(max_length=14, blank=True, null=True)
    details = models.CharField(max_length=50, null=True, blank=True)
    room = models.CharField(max_length=50, null=True, blank=True)
    type = models.IntegerField()

    def __unicode__(self):
        return self.hostname

