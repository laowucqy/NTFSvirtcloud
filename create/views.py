# coding: utf-8
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from server.models import Compute
from flavor.models import Flavor
from create.forms import  NewVMForm
from instances.models import Instance
from vrtManager.create import wvmCreate
from vrtManager import util
from libvirt import libvirtError
from django.db.models import Q
from wuser.user_api import *
from pprint import pprint

@require_role('super')
def create_instance(request, compute_id,create_type):
    """
    :param request:
    :return:
    """

    header_title, path1, path2 = u'通过flavor创建', u'虚拟资源管理', u'规格列表'
    posts = Flavor.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = Flavor.objects.filter(Q(label__contains=keyword))
    else:
        posts = Flavor.objects.exclude(label='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)


    conn = None
    error_messages = []
    storages = []
    networks = []
    meta_prealloc = False
    computes = Compute.objects.all()
    compute = get_object_or_404(Compute, pk=compute_id)

    try:
        conn = wvmCreate(compute.hostname,
                         compute.login,
                         compute.password,
                         compute.type)

        storages = sorted(conn.get_storages())
        networks = sorted(conn.get_networks())
        instances = conn.get_instances()
        get_images = sorted(conn.get_storages_images())
        cache_modes = sorted(conn.get_cache_modes().items())
        mac_auto = util.randomMAC()
    except libvirtError as lib_err:
        error_messages.append(lib_err)

    if conn:
        if not storages:
            msg = _("You haven't defined any storage pools")
            error_messages.append(msg)
        if not networks:
            msg = _("You haven't defined any network pools")
            error_messages.append(msg)

        if request.method == 'POST':

            if 'create' in request.POST:

                volumes = {}
                pprint(request.POST)
                form = NewVMForm(request.POST)
                if form.is_valid():

                    data = form.cleaned_data
                    if data['meta_prealloc']:
                        meta_prealloc = True
                    if instances:
                        if data['name'] in instances:
                            msg = _("A virtual machine with this name already exists")
                            error_messages.append(msg)
                    if not error_messages:
                        print "2"
                        if data['hdd_size']:
                            if not data['mac']:
                                error_msg = _("No Virtual Machine MAC has been entered")
                                error_messages.append(error_msg)
                            else:
                                try:
                                    path = conn.create_volume(data['storage'], data['name'], data['hdd_size'],
                                                              metadata=meta_prealloc)
                                    volumes[path] = conn.get_volume_type(path)
                                except libvirtError as lib_err:
                                    error_messages.append(lib_err.message)
                        elif data['template']:
                            templ_path = conn.get_volume_path(data['template'])
                            clone_path = conn.clone_from_template(data['name'], templ_path, metadata=meta_prealloc)
                            volumes[clone_path] = conn.get_volume_type(clone_path)
                        else:
                            if not data['images']:
                                error_msg = _("First you need to create or select an image")
                                error_messages.append(error_msg)
                            else:
                                for vol in data['images'].split(','):
                                    try:
                                        path = conn.get_volume_path(vol)
                                        volumes[path] = conn.get_volume_type(path)
                                    except libvirtError as lib_err:
                                        error_messages.append(lib_err.message)
                        if data['cache_mode'] not in conn.get_cache_modes():
                            error_msg = _("Invalid cache mode")
                            error_messages.append(error_msg)
                        if not error_messages:

                            uuid = util.randomUUID()
                            try:
                                conn.create_instance(data['name'], data['memory'], data['vcpu'], data['host_model'],
                                                     uuid, volumes, data['cache_mode'], data['networks'], data['virtio'],
                                                     data['mac'])
                                create_instance = Instance(compute_id=compute_id, name=data['name'], uuid=uuid)
                                create_instance.save()
                                return HttpResponseRedirect(reverse('instance', args=[compute_id, data['name']]))
                            except libvirtError as lib_err:
                                if data['hdd_size']:
                                    conn.delete_volume(volumes.keys()[0])
                                error_messages.append(lib_err)

        conn.close()
    if create_type == "1":
        return render(request, 'create/create_instance_1.html', locals())
    elif create_type == "2":
        pass
    elif create_type=="3":
        pass
    return render(request, 'create/create_instance_1.html', locals())


@require_role('super')
def create_from_flavor(request,compute_id,flavor):

    header_title, path1, path2 = u'通过flavor创建', u'虚拟资源管理', u'规格列表'

    flavor = get_object_or_404(Flavor,pk = flavor)
    post = {}
    post['memory'] = flavor.memory
    post['vcpu'] = flavor.vcpu
    post['disk'] = flavor.disk
    conn = None
    error_messages = []
    storages = []
    networks = []
    meta_prealloc = False
    computes = Compute.objects.all()
    compute = get_object_or_404(Compute, pk=compute_id)

    try:
        conn = wvmCreate(compute.hostname,
                         compute.login,
                         compute.password,
                         compute.type)

        storages = sorted(conn.get_storages())
        networks = sorted(conn.get_networks())
        instances = conn.get_instances()
        get_images = sorted(conn.get_storages_images())
        cache_modes = sorted(conn.get_cache_modes().items())
        mac_auto = util.randomMAC()
    except libvirtError as lib_err:
        error_messages.append(lib_err)

    if conn:
        if not storages:
            msg = _("You haven't defined any storage pools")
            error_messages.append(msg)
        if not networks:
            msg = _("You haven't defined any network pools")
            error_messages.append(msg)

        if request.method == 'POST':

            if 'create' in request.POST:
                print "yes"
                volumes = {}
                pprint(request.POST)
                form = NewVMForm(request.POST)
                if form.is_valid():

                    data = form.cleaned_data
                    if data['meta_prealloc']:
                        meta_prealloc = True
                    if instances:
                        if data['name'] in instances:
                            msg = _("A virtual machine with this name already exists")
                            error_messages.append(msg)
                    if not error_messages:
                        print "2"
                        if data['hdd_size']:
                            if not data['mac']:
                                error_msg = _("No Virtual Machine MAC has been entered")
                                error_messages.append(error_msg)
                            else:
                                try:
                                    path = conn.create_volume(data['storage'], data['name'], data['hdd_size'],
                                                              metadata=meta_prealloc)
                                    volumes[path] = conn.get_volume_type(path)
                                except libvirtError as lib_err:
                                    error_messages.append(lib_err.message)
                        elif data['template']:
                            templ_path = conn.get_volume_path(data['template'])
                            clone_path = conn.clone_from_template(data['name'], templ_path, metadata=meta_prealloc)
                            volumes[clone_path] = conn.get_volume_type(clone_path)
                        else:
                            if not data['images']:
                                error_msg = _("First you need to create or select an image")
                                error_messages.append(error_msg)
                            else:
                                for vol in data['images'].split(','):
                                    try:
                                        path = conn.get_volume_path(vol)
                                        volumes[path] = conn.get_volume_type(path)
                                    except libvirtError as lib_err:
                                        error_messages.append(lib_err.message)
                        if data['cache_mode'] not in conn.get_cache_modes():
                            error_msg = _("Invalid cache mode")
                            error_messages.append(error_msg)
                        if not error_messages:

                            uuid = util.randomUUID()
                            try:
                                conn.create_instance(data['name'], data['memory'], data['vcpu'], data['host_model'],
                                                     uuid, volumes, data['cache_mode'], data['networks'],
                                                     data['virtio'],
                                                     data['mac'])
                                create_instance = Instance(compute_id=compute_id, name=data['name'], uuid=uuid)
                                create_instance.save()
                                return HttpResponseRedirect(reverse('instance', args=[compute_id, data['name']]))
                            except libvirtError as lib_err:
                                if data['hdd_size']:
                                    conn.delete_volume(volumes.keys()[0])
                                error_messages.append(lib_err)

        conn.close()

    return render(request, 'create/create_from_flavor.html', locals())