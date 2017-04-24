# coding: utf-8
from django.db import models


class Flavor(models.Model):
    label = models.CharField(max_length=12,verbose_name=u"名称")
    memory = models.IntegerField(verbose_name=u"内存")
    vcpu = models.IntegerField(verbose_name=u"CPU个数")
    disk = models.IntegerField(verbose_name=u"磁盘")

    def __unicode__(self):
        return self.name
