# coding: utf-8
from django.shortcuts import render
from django.db.models import Q
from wuser.user_api import *
from models import Flavor
from forms import FlavorForm
# Create your views here.

# @require_role('super')
# def flavor_list(request):
#     header_title, path1, path2 = u'规格列表', u'虚拟资源管理', u'规格列表'
#     flavor_list =  Flavor.objects.filter().order_by('label')
#     error_messages = []
#     if request.method == 'POST':
#
#         flavor_form = FlavorForm(request.POST,instance=flavor_list)
#         if flavor_form.is_valid():
#             # data = server_form.cleaned_data
#             # compute_edit = Compute.objects.get(id=data['host_id'])
#             # compute_edit.name = data['name']
#             # compute_edit.hostname = data['hostname']
#             # compute_edit.login = data['login']
#             # compute_edit.password = data['password']
#             # compute_edit.details = data['details']
#             # compute_edit.save()
#             flavor_form.save()
#             return HttpResponseRedirect(reverse('flavor_list'))
#         else:
#             for msg_err in flavor_form.errors.values():
#                 error_messages.append(msg_err.as_text())
#
#     else:
#         flavor_form = FlavorForm(instance=flavor_list)
#         return my_render('flavor/flavor_list.html', locals(), request)

@require_role('super')
def flavor_add(request):
    """
    IDC add view
    """
    header_title, path1, path2 = u'添加规格', u'虚拟资源管理', u'添加规格'
    if request.method == 'POST':
        flavor_form = FlavorForm(request.POST)
        if flavor_form.is_valid():
            flavor_name = flavor_form.cleaned_data['label']

            if Flavor.objects.filter(label=flavor_name):
                emg = u'添加失败, 此IDC %s 已存在!' % flavor_name
                return my_render('flavor/flavor_add.html', locals(), request)
            else:
                flavor_form.save()
                smg = u'IDC: %s添加成功' % flavor_add
            return HttpResponseRedirect(reverse('flavor_list'))
    else:
        flavor_form = FlavorForm()
    return my_render('flavor/flavor_add.html', locals(), request)

@require_role('admin')
def flavor_list(request):
    """
    IDC list view
    """
    header_title, path1, path2 = u'规格列表', u'虚拟资源管理', u'规格列表'
    posts = Flavor.objects.all()
    keyword = request.GET.get('keyword', '')
    if keyword:
        posts = Flavor.objects.filter(Q(label__contains=keyword) )
    else:
        posts = Flavor.objects.exclude(label='ALL').order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('flavor/flavor_list.html', locals(), request)

@require_role('super')
def flavor_del(request):
    """
    IDC delete view
    """
    flavor_ids = request.GET.get('id', '')
    flavor_id_list = flavor_ids.split(',')

    for flavor_id in flavor_id_list:
        Flavor.objects.filter(id=flavor_id).delete()

    return HttpResponseRedirect(reverse('flavor_list'))

@require_role('super')
def flavor_edit(request):
    """
    IDC edit view
    """
    header_title, path1, path2 = u'编辑IDC', u'资产管理', u'编辑IDC'
    flavor_id = request.GET.get('id', '')
    flavor = get_object(Flavor, id=flavor_id)
    if request.method == 'POST':
        flavor_form = FlavorForm(request.POST, instance=flavor)
        if flavor_form.is_valid():
            flavor_form.save()
            return HttpResponseRedirect(reverse('flavor_list'))
    else:
        flavor_form = FlavorForm(instance=flavor)
        return my_render('flavor/flavor_edit.html', locals(), request)

