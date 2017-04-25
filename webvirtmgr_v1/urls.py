from django.conf.urls import patterns, include, url
from instances.views import instances
from console.views import console as console_vnc
from create.views import create_instance,create_from_flavor
urlpatterns = patterns('webvirtmgr_v1.views',
                       # Examples:
                       url(r'^$', 'index', name='index'),
                       # url(r'^api/user/$', 'api_user'),
                       url(r'^instances/$', instances, name='instances'),
                       url(r'^compute/(?P<compute_id>[0-9]+)/(?P<create_type>[0-9]+)/create/$',
                           create_instance, name='create_instance'),
                       url(r'^compute/(?P<compute_id>[0-9]+)/(?P<flavor>[0-9]+)/create_from_flavor/$',
                           create_from_flavor, name='create_from_flavor'),
                       url(r'^skin_config/$', 'skin_config', name='skin_config'),
                       url(r'^login/$', 'Login', name='login'),
                       url(r'^logout/$', 'Logout', name='logout'),
                       # url(r'^exec_cmd/$', 'exec_cmd', name='exec_cmd'),
                       # url(r'^file/upload/$', 'upload', name='file_upload'),
                       # url(r'^file/download/$', 'download', name='file_download'),
                       # url(r'^setting', 'setting', name='setting'),
                       # url(r'^terminal/$', 'web_terminal', name='terminal'),
                       url(r'^juser/', include('wuser.urls')),
                       url(r'^flavor/', include('flavor.urls')),
                       url(r'^server/',include('server.urls')),
                       url(r'^instance/',include('instances.urls')),
                       url(r'^console/$', console_vnc, name='console'),
                       # url(r'^jasset/', include('jasset.urls')),
                       # url(r'^jlog/', include('jlog.urls')),
                       # url(r'^jperm/', include('jperm.urls')),
                       )
