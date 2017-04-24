#!/usr/bin/python
# coding: utf-8

import sys
import os
import django
from django.core.management import execute_from_command_line
import shlex
import urllib
import socket
import subprocess


jms_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(jms_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'webvirtmgr_v1.settings'
if django.get_version() != '1.6':
    setup = django.setup()

from wuser.user_api import db_add_user, get_object, User

from webvirtmgr_v1.api import get_mac_address, bash

socket.setdefaulttimeout(2)


class Setup(object):
    """
    安装jumpserver向导
    """

    def __init__(self):
        self.admin_user = 'admin'
        self.admin_pass = '5Lov@wife'



    def _input_admin(self):
        while True:
            print
            admin_user = raw_input('请输入管理员用户名 [%s]: ' % self.admin_user).strip()
            admin_pass = raw_input('请输入管理员密码: [%s]: ' % self.admin_pass).strip()
            admin_pass_again = raw_input('请再次输入管理员密码: [%s]: ' % self.admin_pass).strip()

            if admin_user:
                self.admin_user = admin_user

            if not admin_pass_again:
                admin_pass_again = self.admin_pass

            if admin_pass:
                self.admin_pass = admin_pass

            if self.admin_pass != admin_pass_again:
                print('两次密码不相同请重新输入')
            else:
                break
            print

    @staticmethod
    def _sync_db():
        os.chdir(jms_dir)
        execute_from_command_line(['manage.py', 'syncdb', '--noinput'])

    def _create_admin(self):
        user = get_object(User, username=self.admin_user)
        if user:
            user.delete()
        db_add_user(username=self.admin_user, password=self.admin_pass, role='SU', name='admin', groups='',
                    admin_groups='', email='admin@jumpserver.org', uuid='MayBeYouAreTheFirstUser', is_active=True)
        cmd = 'id %s 2> /dev/null 1> /dev/null || useradd %s' % (self.admin_user, self.admin_user)
        shlex.os.system(cmd)

    @staticmethod
    def _chmod_file():
        os.chdir(jms_dir)
        os.chmod('init.sh', 0755)
        os.chmod('connect.py', 0755)
        os.chmod('manage.py', 0755)
        os.chmod('run_server.py', 0755)
        os.chmod('service.sh', 0755)
        os.chmod('logs', 0777)
        os.chmod('keys', 0777)



    def start(self):
        print "开始安装Jumpserver ..."
        
        self._input_admin()
        self._create_admin()



if __name__ == '__main__':
    setup = Setup()
    setup.start()
