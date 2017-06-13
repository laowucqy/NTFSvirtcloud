# coding:utf-8
from django.utils.translation import ugettext_lazy as _
from instances.models import Compute
from network.forms import AddNetPool
from vrtManager.network import wvmNetwork, wvmNetworks
from vrtManager.connection import connection_manager
from vrtManager.network import network_size
from libvirt import libvirtError
from wuser.user_api import *
from django.db.models import Q


@require_role('super')
def networks(request):
    """
    Networks block
    """
    header_title, path1, path2 = u'网络列表', u'网络管理', u'网络列表'
    errors = []
    all_host_nets = {}
    # compute = Compute.objects.get(id=host_id)
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
                    conn = wvmNetworks(comp.hostname,
                                       comp.login,
                                       comp.password,
                                       comp.type)
                    networks = conn.get_networks_info()
                    if networks:
                        all_host_nets[comp.id, comp.name] = networks
                    conn.close()
                except libvirtError as lib_err:
                    errors.append(lib_err)

        # print all_host_nets
    except libvirtError as err:
        errors.append(err)

    return render_to_response('network/networks.html', locals(), context_instance=RequestContext(request))


@require_role('super')
def create_network(request,host_id):
    header_title, path1, path2 = u'添加虚拟网络', u'网络管理', u'添加虚拟网络'
    error_messages = []
    compute = Compute.objects.get(id=host_id)
    try:
        conn = wvmNetworks(compute.hostname,
                          compute.login,
                          compute.password,
                          compute.type)
        networks = conn.get_networks_info()
        if 'create' in request.POST:
            form = AddNetPool(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if data['name'] in networks:
                    msg = _("Pool name already in use")
                    error_messages.append(msg)
                if data['forward'] == 'bridge' and data['bridge_name'] == '':
                    error_messages.append('Please enter bridge name')
                try:
                    gateway, netmask, dhcp = network_size(data['subnet'], data['dhcp'])
                except:
                    msg = _("Input subnet pool error")
                    error_messages.append(msg)
                if not error_messages:
                    conn.create_network(data['name'], data['forward'], gateway, netmask,
                                        dhcp, data['bridge_name'], data['openvswitch'], data['fixed'])
                    return HttpResponseRedirect(reverse('networks'))
        conn.close()
    except libvirtError as err:
        error_messages.append(err)

    return render_to_response('network/create_network.html', locals(), context_instance=RequestContext(request))


@require_role('super')
def network(request, host_id, pool):
    """
    Networks block
    """
    header_title, path1, path2 = u'虚拟网络详情', u'网络管理', u'虚拟网络详情'
    errors = []
    compute = Compute.objects.get(id=host_id)

    try:
        conn = wvmNetwork(compute.hostname,
                          compute.login,
                          compute.password,
                          compute.type,
                          pool)
        networks = conn.get_networks()
        state = conn.is_active()
        device = conn.get_bridge_device()
        autostart = conn.get_autostart()
        ipv4_forward = conn.get_ipv4_forward()
        ipv4_dhcp_range_start = conn.get_ipv4_dhcp_range_start()
        ipv4_dhcp_range_end = conn.get_ipv4_dhcp_range_end()
        ipv4_network = conn.get_ipv4_network()
        fixed_address = conn.get_mac_ipaddr()
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
                return HttpResponseRedirect(reverse('networks', args=[host_id]))
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

    conn.close()

    return render_to_response('network/network.html', locals(), context_instance=RequestContext(request))
