# coding: utf-8
from django.db import models
from server.models import Compute

class Project(models.Model):
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=160, blank=True, null=True)
    #group = models.ManyToManyField(UserGroup)

    def __unicode__(self):
        return self.name


class Instance(models.Model):
    compute = models.ForeignKey(Compute)
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=80)
    is_template = models.BooleanField(default=False)
    project = models.ManyToManyField(Project)

    def __unicode__(self):
        return self.name



# Create your models here.
