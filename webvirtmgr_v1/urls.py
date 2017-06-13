from django.conf.urls import patterns, include, url
from instances.views import instances
from console.views import console as console_vnc
from create.views import create_from_template,create_from_flavor
urlpatterns = patterns('webvirtmgr_v1.views',
                       # Examples:
                       url(r'^$', 'index', name='index'),
                       # url(r'^api/user/$', 'api_user'),
                       url(r'^instances/$', instances, name='instances'),
                       url(r'^compute/(?P<compute_id>[0-9]+)/create_from_template/$',
                           create_from_template, name='create_from_template'),
                       url(r'^compute/(?P<compute_id>[0-9]+)/(?P<flavor>[0-9]+)/create_from_flavor/$',
                           create_from_flavor, name='create_from_flavor'),
                       url(r'^skin_config/$', 'skin_config', name='skin_config'),
                       url(r'^login/$', 'Login', name='login'),
                       url(r'^logout/$', 'Logout', name='logout'),
                       url(r'^juser/', include('wuser.urls')),
                       url(r'^flavor/', include('flavor.urls')),
                       url(r'^server/',include('server.urls')),
                       url(r'^instance/',include('instances.urls')),
                       url(r'^network/',include('network.urls')),
                       url(r'^storages/',include('storage.urls')),
                       url(r'^project/',include('project.urls')),
                       url(r'^console/$', console_vnc, name='console'),
                       )
