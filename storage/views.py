# coding:utf-8
from django.utils.translation import ugettext_lazy as _
from instances.models import Compute
from storage.forms import AddStgPool, AddImage, CloneImage
from vrtManager.storage import wvmStorage, wvmStorages
from libvirt import libvirtError
from wuser.user_api import *
from django.db.models import Q
from vrtManager.connection import connection_manager

@require_role('super')
def storages(request):
    """
    Storage pool block
    """
    header_title, path1, path2 = u'磁盘列表', u'磁盘管理', u'磁盘列表'
    error_messages = []
    all_host_storages = {}
    computes = Compute.objects.all()

    def get_hosts_status(computes):
        """
        Function return all hosts all vds on host
        """
        compute_data = []
        for compute in computes:
            compute_data.append({'id': compute.id,
                                 'name': compute.name,
                                 'hostname': compute.hostname,
                                 'status': connection_manager.host_is_up(compute.type, compute.hostname),
                                 'type': compute.type,
                                 'login': compute.login,
                                 'password': compute.password,
                                 'details': compute.details
                                 })
        return compute_data


    try:

        keyword = request.GET.get('keyword', '')
        computes = Compute.objects.filter().order_by('name')
        if keyword:
            computes = computes.filter(Q(name__icontains=keyword) | Q(hostname__icontains=keyword)).order_by('name')
        computes_info = get_hosts_status(computes)
        computes_info, p, compute, page_range, current_page, show_first, show_end = pages(computes_info, request)
        for comp in computes:
            if connection_manager.host_is_up(comp.type, comp.hostname):
                try:
                    conn = wvmStorages(comp.hostname,
                                       comp.login,
                                       comp.password,
                                       comp.type)
                    storages = conn.get_storages_info()
                    secrets = conn.get_secrets()
                    if storages:
                        all_host_storages[comp.id, comp.name] =storages
                    conn.close()
                except libvirtError as lib_err:
                    error_messages.append(lib_err)

    except libvirtError as err:
        error_messages.append(err)

    return render_to_response('storage/storages.html', locals(), context_instance=RequestContext(request))



@require_role('super')
def storage(request, host_id, pool):
    """
    Storage pool block
    """
    header_title, path1, path2 = u'磁盘详情', u'磁盘管理', u'磁盘详情'
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    def handle_uploaded_file(path, f_name):
        target = path + '/' + str(f_name)
        destination = open(target, 'wb+')
        for chunk in f_name.chunks():
            destination.write(chunk)
        destination.close()

    errors = []
    compute = Compute.objects.get(id=host_id)
    meta_prealloc = False

    try:
        conn = wvmStorage(compute.hostname,
                          compute.login,
                          compute.password,
                          compute.type,
                          pool)

        storages = conn.get_storages()
        state = conn.is_active()
        size, free = conn.get_size()
        used = (size - free)
        if state:
            percent = (used * 100) / size
        else:
            percent = 0
        status = conn.get_status()
        path = conn.get_target_path()
        type = conn.get_type()
        autostart = conn.get_autostart()

        if state:
            conn.refresh()
            volumes = conn.update_volumes()
        else:
            volumes = None
    except libvirtError as err:
        errors.append(err)

    if request.method == 'POST':
        if 'start' in request.POST:
            try:
                conn.start()
                return HttpResponseRedirect(request.get_full_path())
            except libvirtError as error_msg:
                errors.append(error_msg.message)
        if 'stop' in request.POST:
            try:
                conn.stop()
                return HttpResponseRedirect(request.get_full_path())
            except libvirtError as error_msg:
                errors.append(error_msg.message)
        if 'delete' in request.POST:
            try:
                conn.delete()
                return HttpResponseRedirect(reverse('storages', args=[host_id]))
            except libvirtError as error_msg:
                errors.append(error_msg.message)
        if 'set_autostart' in request.POST:
            try:
                conn.set_autostart(1)
                return HttpResponseRedirect(request.get_full_path())
            except libvirtError as error_msg:
                errors.append(error_msg.message)
        if 'unset_autostart' in request.POST:
            try:
                conn.set_autostart(0)
                return HttpResponseRedirect(request.get_full_path())
            except libvirtError as error_msg:
                errors.append(error_msg.message)
        if 'add_volume' in request.POST:
            form = AddImage(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['meta_prealloc'] and data['format'] == 'qcow2':
                    meta_prealloc = True
                try:
                    conn.create_volume(data['name'], data['size'], data['format'], meta_prealloc)
                    return HttpResponseRedirect(request.get_full_path())
                except libvirtError as err:
                    errors.append(err)
        if 'del_volume' in request.POST:
            volname = request.POST.get('volname', '')
            try:
                vol = conn.get_volume(volname)
                vol.delete(0)
                return HttpResponseRedirect(request.get_full_path())
            except libvirtError as error_msg:
                errors.append(error_msg.message)
        if 'iso_upload' in request.POST:
            if str(request.FILES['file']) in conn.update_volumes():
                msg = _("ISO image already exist")
                errors.append(msg)
            else:
                handle_uploaded_file(path, request.FILES['file'])
                return HttpResponseRedirect(request.get_full_path())
        if 'cln_volume' in request.POST:
            form = CloneImage(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                img_name = data['name'] + '.img'
                meta_prealloc = 0
                if img_name in conn.update_volumes():
                    msg = _("Name of volume name already use")
                    errors.append(msg)
                if not errors:
                    if data['convert']:
                        format = data['format']
                        if data['meta_prealloc'] and data['format'] == 'qcow2':
                            meta_prealloc = True
                    else:
                        format = None
                    try:
                        conn.clone_volume(data['image'], data['name'], format, meta_prealloc)
                        return HttpResponseRedirect(request.get_full_path())
                    except libvirtError as err:
                        errors.append(err)
    conn.close()

    return render_to_response('storage/storage.html', locals(), context_instance=RequestContext(request))
