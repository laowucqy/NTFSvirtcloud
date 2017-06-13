# coding: utf-8

from wuser.user_api import *
from instances.models import Project
from instances.models import Instance
from django.shortcuts import get_object_or_404
from django.db.models import Q
# Create your views here.
from pprint import  pprint


@require_role(role='super')
def project_del(request):
    """
    del a group
    删除用户组
    """
    project_ids = request.GET.get('id', '')
    project_id_list = project_ids.split(',')
    for project_id in project_id_list:
        Project.objects.filter(id=project_id).delete()

    return HttpResponse('删除成功')


@require_role(role='super')
def project_edit(request):
    error = ''
    msg = ''
    header_title, path1, path2 = '编辑项目', '项目管理', '编辑项目'

    if request.method == 'GET':
        project_id = request.GET.get('id', '')
        project = get_object(Project, id=project_id)
        # user_group = UserGroup.objects.get(id=group_id)
        instances_selected = Instance.objects.filter(project=project)
        instances_remain = Instance.objects.filter(~Q(project=project))
        instances_all = Instance.objects.all()

    elif request.method == 'POST':
        project_id = request.POST.get('project_id', '')
        project_name = request.POST.get('project_name', '')
        comment = request.POST.get('comment', '')
        instances_selected = request.POST.getlist('instances_selected')

        try:
            if '' in [project_id, project_name]:
                raise ServerError('项目名不能为空')

            if len(Project.objects.filter(name=project_name)) > 1:
                raise ServerError(u'%s 项目已存在' % project_name)
            # add user group
            project = get_object_or_404(Project, id=project_id)
            project.instance_set.clear()

            for instance in Instance.objects.filter(id__in=instances_selected):
                instance.project.add(Project.objects.get(id=project_id))

            project.name = project_name
            project.comment = comment
            project.save()
            # pprint(project)
        except ServerError, e:
            error = e

        if not error:
            return HttpResponseRedirect(reverse('projects'))
        else:
            instances_all = Instance.objects.all()
            instances_selected = Instance.objects.filter(project=project)
            instances_remain = Instance.objects.filter(~Q(project=project))

    return my_render('project/project_edit.html', locals(), request)



@require_role(role='super')
def project_list(request):
    """
    list user group
    用户组列表
    """
    header_title, path1, path2 = '查看项目', '项目管理', '查看项目'
    keyword = request.GET.get('search', '')
    project_list = Project.objects.all().order_by('name')
    # user_group_list = UserGroup.objects.all().order_by('name')
    #group_id = request.GET.get('id', '')


    # if keyword:
    #     user_group_list = user_group_list.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword))
    #
    # if group_id:
    #     user_group_list = user_group_list.filter(id=int(group_id))

    # user_group_list, p, user_groups, page_range, current_page, show_first, show_end = pages(user_group_list, request)
    return my_render('project/projects.html', locals(), request)


@require_role(role='super')
def project_add(request):
    """
    group add view for route
    添加用户组的视图
    """
    error = ''
    msg = ''
    header_title, path1, path2 = '添加项目', '用户项目', '添加项目'
    #user_all = User.objects.all()
    instance_all = Instance.objects.all()

    if request.method == 'POST':
        project_name = request.POST.get('project_name', '')
        instances_selected = request.POST.getlist('instances_selected', '')
        comment = request.POST.get('comment','')

        # group_name = request.POST.get('group_name', '')
        # users_selected = request.POST.getlist('users_selected', '')
        # comment = request.POST.get('comment', '')

        try:
            if not project_name:
                error = u'项目名 不能为空'
                raise ServerError(error)

            if Project.objects.filter(name=project_name):
                error = u'项目名已存在'
                raise ServerError(error)
            db_add_project(name=project_name, instances_id=instances_selected, comment=comment)
        except ServerError:
            pass
        except TypeError:
            error = u'添加项目失败'
        else:
            msg = u'添加项目 %s 成功' % project_name

    return my_render('project/project_add.html', locals(), request)


def project_add_instance(project, instance_id=None, instance_name=None):
    """
    用户组中添加用户
    UserGroup Add a user
    """
    if instance_id:
        instance = get_object(Instance, id=instance_id)
    else:
        instance = get_object(Instance, name=instance_name)

    if instance:
        print(instance_id)
        project.instance_set.add(instance)


def db_add_project(**kwargs):
    """
    add a user group in database
    数据库中添加用户组
    """
    name = kwargs.get('name')
    project = get_object(Project, name=name)
    instances = kwargs.pop('instances_id')

    if not project:
        project = Project(**kwargs)
        project.save()
        for instance_id in instances:
            project_add_instance(project, instance_id)

# def group_add_user(group, user_id=None, username=None):
#     """
#     用户组中添加用户
#     UserGroup Add a user
#     """
#     if user_id:
#         user = get_object(User, id=user_id)
#     else:
#         user = get_object(User, username=username)
#
#     if user:
#         group.user_set.add(user)
#
#
# def db_add_group(**kwargs):
#     """
#     add a user group in database
#     数据库中添加用户组
#     """
#     name = kwargs.get('name')
#     group = get_object(UserGroup, name=name)
#     users = kwargs.pop('users_id')
#
#     if not group:
#         group = UserGroup(**kwargs)
#         group.save()
#         for user_id in users:
#             group_add_user(group, user_id)