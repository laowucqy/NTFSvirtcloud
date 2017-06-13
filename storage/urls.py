from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^storages/$', views.storages, name='storages'),
    # url(r'^(?P<host_id>[0-9]+)/create/$',
    #     views.create_network, name='create_network'),
    url(r'^(?P<host_id>[0-9]+)/(?P<pool>[\w\-\.]+)/$',
        views.storage, name='storage'),
]
