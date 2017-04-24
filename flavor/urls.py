# coding:utf-8
from django.conf.urls import patterns, include, url
from flavor.views import *

urlpatterns = patterns('',
                       # url(r'^server/list/$', computes, name='server_list'),
                       # url(r'^server/add/$', server_add, name='server_add'),
                       # url(r'^server/del/$', server_del, name='server_del'),
                       # url(r'^server/edit/$', server_edit, name='server_edit'),
                       # url(r'^server/detail/$', computes, name='server_detail'),
                       url(r'^flavor/list/$', flavor_list, name='flavor_list'),
                       url(r'^flavor/add/$', flavor_add, name='flavor_add'),
                       url(r'^flavor/del/$', flavor_del, name='flavor_del'),
                       url(r'^flavor/edit/$', flavor_edit, name='flavor_edit'),


                       )