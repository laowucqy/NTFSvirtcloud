# coding: utf-8

from django.db import models
from django.contrib.auth.models import AbstractUser
import time
from instances.models import Instance
# from jasset.models import Asset, AssetGroup


class UserGroup(models.Model):
    name = models.CharField(max_length=80, unique=True)
    comment = models.CharField(max_length=160, blank=True, null=True)

    def __unicode__(self):
        return self.name


class User(AbstractUser):
    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('GA', 'GroupAdmin'),
        ('CU', 'CommonUser'),
    )
    name = models.CharField(max_length=80)
    uuid = models.CharField(max_length=100)
    role = models.CharField(max_length=2, choices=USER_ROLE_CHOICES, default='CU')
    group = models.ManyToManyField(UserGroup)
    ssh_key_pwd = models.CharField(max_length=200)
    # is_active = models.BooleanField(default=True)
    # last_login = models.DateTimeField(null=True)
    # date_joined = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.username


class AdminGroup(models.Model):
    """
    under the user control group
    用户可以管理的用户组，或组的管理员是该用户
    """

    user = models.ForeignKey(User)
    group = models.ForeignKey(UserGroup)

    def __unicode__(self):
        return '%s: %s' % (self.user.username, self.group.name)


class Document(models.Model):
    def upload_to(self, filename):
        return 'upload/'+str(self.user.id)+time.strftime('/%Y/%m/%d/', time.localtime())+filename

    docfile = models.FileField(upload_to=upload_to)
    user = models.ForeignKey(User)

class UserInstance(models.Model):
    user = models.ForeignKey(User)
    instance = models.ForeignKey(Instance)
    is_change = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_vnc = models.BooleanField(default=False)

    def __unicode__(self):
        return self.instance.name


class UserSSHKey(models.Model):
    user = models.ForeignKey(User)
    keyname = models.CharField(max_length=25)
    keypublic = models.CharField(max_length=500)

    def __unicode__(self):
        return self.keyname

class UserAttributes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_clone_instances = models.BooleanField(default=False)
    max_instances = models.IntegerField(default=1)
    max_cpus = models.IntegerField(default=1)
    max_memory = models.IntegerField(default=2048)
    max_disk_size = models.IntegerField(default=20)

    def __unicode__(self):
        return self.user.username
