# coding:utf-8
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from server.models import Compute
from instances.models import Instance
from wuser.models import UserInstance
from server.forms import ComputeAddSshForm, ServerForm
from vrtManager.hostdetails import wvmHostDetails
from vrtManager.connection import CONN_SSH, CONN_TCP, CONN_TLS, CONN_SOCKET, connection_manager
from libvirt import libvirtError
from django.db.models import Q
from wuser.user_api import *

@require_role('super')
def computes(request):
    """
    :param request:
    :return:
    """
    header_title, path1, path2 = u'物理机列表', u'物理机管理', u'物理机列表'

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
            print connection_manager.host_is_up(compute.type, compute.hostname)
        return compute_data

    keyword = request.GET.get('keyword', '')
    error_messages = []
    computes = Compute.objects.filter().order_by('name')
    if keyword:
        computes = computes.filter(Q(name__icontains=keyword) | Q(hostname__icontains=keyword)).order_by('name')
    computes_info = get_hosts_status(computes)
    computes_info, p, servers, page_range, current_page, show_first, show_end = pages(computes_info, request)
    return my_render( 'server/server_list.html', locals(),request)

@require_role('super')
def server_add(request):

    header_title, path1, path2 = u'添加物理机', u'物理机管理', u'添加物理机'
    error_messages = []
    if request.method == 'POST':
        form = ComputeAddSshForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_ssh_host = Compute(name=data['name'],
                                   hostname=data['hostname'],
                                   type=CONN_SSH,
                                   login=data['login'])
            new_ssh_host.save()
            # return HttpResponseRedirect(request.get_full_path())
            return HttpResponseRedirect(reverse('server_list'))
        else:
            for msg_err in form.errors.values():
                error_messages.append(msg_err.as_text())

    return my_render('server/server_add.html', locals(), request)


@require_role('super')
def server_del(request):
    header_title, path1, path2 = u'物理机列表', u'物理机管理', u'物理机列表'
    compute_id = request.GET.get('id', '')
    try:
        del_user_inst_on_host = UserInstance.objects.filter(instance__compute_id=compute_id)
        del_user_inst_on_host.delete()
    finally:
        try:
            del_inst_on_host = Instance.objects.filter(compute_id=compute_id)
            del_inst_on_host.delete()
        finally:
            del_host = Compute.objects.get(id=compute_id)
            del_host.delete()

    return HttpResponseRedirect(reverse('server_list'))



@require_role('super')
def server_edit(request):
    header_title, path1, path2 = u'编辑物理机', u'物理机管理', u'编辑物理机'
    compute_id = request.GET.get('id', '')
    edit_host =  Compute.objects.get(id=compute_id)
    error_messages = []
    if request.method == 'POST':

        server_form = ServerForm(request.POST,instance=edit_host)
        if server_form.is_valid():
            # data = server_form.cleaned_data
            # compute_edit = Compute.objects.get(id=data['host_id'])
            # compute_edit.name = data['name']
            # compute_edit.hostname = data['hostname']
            # compute_edit.login = data['login']
            # compute_edit.password = data['password']
            # compute_edit.details = data['details']
            # compute_edit.save()
            server_form.save()
            return HttpResponseRedirect(reverse('server_list'))
        else:
            for msg_err in server_form.errors.values():
                error_messages.append(msg_err.as_text())

    else:
        server_form = ServerForm(instance=edit_host)
        return my_render('server/server_edit.html', locals(), request)

@login_required
def overview(request, compute_id):
    """
    :param request:
    :return:
    """

    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('index'))

    error_messages = []
    compute = get_object_or_404(Compute, pk=compute_id)

    try:
        conn = wvmHostDetails(compute.hostname,
                              compute.login,
                              compute.password,
                              compute.type)
        hostname, host_arch, host_memory, logical_cpu, model_cpu, uri_conn = conn.get_node_info()
        hypervisor = conn.hypervisor_type()
        mem_usage = conn.get_memory_usage()
        conn.close()
    except libvirtError as lib_err:
        error_messages.append(lib_err)

    return render(request, 'overview.html', locals())


@login_required
def compute_graph(request, compute_id):
    """
    :param request:
    :return:
    """

    points = 5
    datasets = {}
    cookies = {}
    compute = get_object_or_404(Compute, pk=compute_id)
    curent_time = time.strftime("%H:%M:%S")

    try:
        conn = wvmHostDetails(compute.hostname,
                              compute.login,
                              compute.password,
                              compute.type)
        cpu_usage = conn.get_cpu_usage()
        mem_usage = conn.get_memory_usage()
        conn.close()
    except libvirtError:
        cpu_usage = 0
        mem_usage = 0

    try:
        cookies['cpu'] = request.COOKIES['cpu']
        cookies['mem'] = request.COOKIES['mem']
        cookies['timer'] = request.COOKIES['timer']
    except KeyError:
        cookies['cpu'] = None
        cookies['mem'] = None

    if not cookies['cpu'] or not cookies['mem']:
        datasets['cpu'] = [0] * points
        datasets['mem'] = [0] * points
        datasets['timer'] = [0] * points
    else:
        datasets['cpu'] = eval(cookies['cpu'])
        datasets['mem'] = eval(cookies['mem'])
        datasets['timer'] = eval(cookies['timer'])

    datasets['timer'].append(curent_time)
    datasets['cpu'].append(int(cpu_usage['usage']))
    datasets['mem'].append(int(mem_usage['usage']) / 1048576)

    if len(datasets['timer']) > points:
        datasets['timer'].pop(0)
    if len(datasets['cpu']) > points:
        datasets['cpu'].pop(0)
    if len(datasets['mem']) > points:
        datasets['mem'].pop(0)

    data = json.dumps({'cpudata': datasets['cpu'], 'memdata': datasets['mem'], 'timeline': datasets['timer']})
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.cookies['cpu'] = datasets['cpu']
    response.cookies['timer'] = datasets['timer']
    response.cookies['mem'] = datasets['mem']
    response.write(data)
    return response
