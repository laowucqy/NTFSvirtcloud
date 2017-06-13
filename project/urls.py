
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^projects/$', views.project_list, name='projects'),
    url(r'^add/$', views.project_add, name='project_add'),
    url(r'^delete/$', views.project_del, name='project_del'),
    url(r'^edit/$', views.project_edit, name='project_edit'),
    # url(r'^(?P<host_id>[0-9]+)/(?P<pool>[\w\-\.]+)/$',
    #     views.storage, name='storage'),
]
