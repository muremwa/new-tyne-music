from typing import List, Set
import logging

from django.shortcuts import render
from django.urls import reverse
from django.views import View, generic
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.messages import add_message, constants as message_constants

from .staff_actions import staff_actions
from .models import HelpArticle
from .forms import HelpArticleForm, HelpArticleEditForm
from core.models import User
from tyne_utils.funcs import is_string_true_or_false
from .logs_processing import log_action_ids


staff_logger = logging.getLogger('tyne.staff')


def info_log_staff_message(action_id, message):
    staff_logger.info(f'ID: {action_id}:{message}')


class StaffAccessMixin(UserPassesTestMixin):
    def test_func(self):
        if hasattr(self, 'request'):
            return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        raise Http404


class StaffPermissionMixin(PermissionRequiredMixin):
    def handle_no_permission(self):
        raise Http404


class StaffHome(StaffAccessMixin, generic.TemplateView):
    template_name = 'staff/staff_home.html'

    def user_has_perm(self, perm: str) -> bool:
        return self.request.user.has_perm(perm)

    def include_action(self, action_perms: List) -> bool:
        return all([self.user_has_perm(perm) for perm in action_perms])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'staff_actions': [action for action in staff_actions if self.include_action(action.get('permissions'))]
        })
        return context


class AddAdminUsers(StaffAccessMixin, StaffPermissionMixin, View):
    template = 'staff/add_user.html'
    permission_required = (
        'auth.change_group', 'auth.view_group', 'auth.change_permission', 'auth.view_permission',
        'core.change_user', 'core.view_user'
    )

    def log_message_user(self):
        return f'{self.request.user.username}({self.request.user.pk})'

    def add_user_to_group(self, user: User, group_pk: int) -> bool:
        try:
            group = Group.objects.get(pk=group_pk)
            user.groups.add(group)
            added = True
            user_info = f'{user.username}({user.pk})'
            info_log_staff_message(
                log_action_ids.ADD_TO_GROUP,
                f'{self.log_message_user()}) added {user_info} to {group.name}'
            )
        except ObjectDoesNotExist:
            added = False
        return added

    def remove_user_from_staff(self, user):
        user.groups.clear()
        user.is_staff = False
        user.save()
        user_info = f'{user.username}({user.pk})'
        info_log_staff_message(
            log_action_ids.REMOVE_STAFF,
            f'{self.log_message_user()} removed {user_info} from staff'
        )

    def make_user_staff(self, user):
        user.is_staff = True
        user.save()
        info_log_staff_message(
            log_action_ids.ADD_STAFF,
            f'{self.log_message_user()} made {user.username}({user.pk}) staff'
        )

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        email = request.POST.get('email', '')
        manage = None
        email_not_found = False
        message = None
        user_info = ''

        try:
            manage = User.objects.get(email=email)
            user_info = f'{manage.username}({manage.pk})'
        except ObjectDoesNotExist:
            email_not_found = True

        if email == request.user.email:
            manage = None
            email_not_found = True
            message = 'You have yourself to blame'

        # make staff
        make_staff = request.POST.get('make-staff', '0')
        if is_string_true_or_false(make_staff) and manage and not manage.is_staff:
            self.make_user_staff(manage)
            message = f'Added \'{manage.username}\' to staff'

        # remove from staff
        remove_staff = request.POST.get('remove-staff', '0')
        if is_string_true_or_false(remove_staff) and manage and manage.is_staff:
            self.remove_user_from_staff(manage)
            message = f'Removed \'{manage.username} from staff\''

        # add to group
        add_to_group = request.POST.get('group-add', '')
        if add_to_group and add_to_group.isdigit() and manage:
            add_to_group_result = self.add_user_to_group(group_pk=add_to_group, user=manage)
            if add_to_group_result:
                message = f'\'{manage.username}\' added to group ID {add_to_group}'

        # remove from group
        remove_from_group = request.POST.get('group-remove', '')
        if remove_from_group and remove_from_group.isdigit() and manage:
            manage.groups.remove(remove_from_group)
            message = f'\'{manage.username}\' removed from group ID {remove_from_group}'
            info_log_staff_message(
                log_action_ids.REMOVE_FROM_GROUP,
                f'{self.log_message_user()} removed {user_info} from group({remove_from_group})'
            )

        if message:
            add_message(request, message_constants.SUCCESS, message=message)

        return render(request, self.template, {
            'email': email,
            'manage': manage,
            'email_not_found': email_not_found,
            'groups': Group.objects.all(),
        })


class StaffHelpList(StaffAccessMixin, generic.ListView):
    queryset = HelpArticle.objects.filter(is_staff=True).order_by('-id')
    context_object_name = 'articles'
    template_name = 'staff/help_list.html'

    def get_queryset(self):
        q_set = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            q_set = q_set.filter((Q(title__icontains=query) | Q(description__icontains=query)))
        return q_set


class StaffHelpArticlePage(StaffAccessMixin, generic.DetailView):
    queryset = HelpArticle.objects.all()
    slug_url_kwarg = 'article_slug'
    context_object_name = 'article'
    template_name = 'staff/help_detail.html'


class StaffArticleAdd(StaffAccessMixin, PermissionRequiredMixin, generic.CreateView):
    model = HelpArticle
    form_class = HelpArticleForm
    template_name = 'staff/article_edit.html'
    permission_required = ('staff.add_helparticle',)

    def get_success_url(self):
        user_info = f'{self.request.user.username}({self.request.user.pk})'
        info_log_staff_message(
            log_action_ids.CREATE_ARTICLE,
            f'{user_info} created article {self.object.title}({self.object.pk})'
        )
        return reverse("staff:help-article", kwargs={"article_slug": str(self.object.slug)})


class StaffArticleEdit(StaffAccessMixin, PermissionRequiredMixin, generic.UpdateView):
    model = HelpArticle
    form_class = HelpArticleEditForm
    template_name = 'staff/article_edit.html'
    pk_url_kwarg = 'article_pk'
    context_object_name = 'article'
    permission_required = ('staff.change_helparticle',)

    def get_success_url(self):
        user_info = f'{self.request.user.username}({self.request.user.pk})'
        info_log_staff_message(
            log_action_ids.EDIT_ARTICLE,
            f'{user_info} edited article {self.object.title}({self.object.pk})'
        )
        return reverse("staff:help-article", kwargs={"article_slug": str(self.object.slug)})


class StaffArticleHelpDelete(StaffAccessMixin, PermissionRequiredMixin, generic.DeleteView):
    model = HelpArticle
    pk_url_kwarg = 'article_pk'
    context_object_name = 'article'
    permission_required = ('staff.delete_helparticle',)

    def get_success_url(self):
        user_info = f'{self.request.user.username}({self.request.user.pk})'
        info_log_staff_message(
            log_action_ids.DELETE_ARTICLE,
            f'{user_info} deleted article {self.object.title}({self.object.pk})'
        )
        return reverse("staff:help-list")


class StaffRolesView(StaffAccessMixin, StaffPermissionMixin, generic.TemplateView):
    template_name = 'staff/staff_roles.html'
    permission_required = (
        'auth.change_group', 'auth.view_group', 'auth.change_permission', 'auth.view_permission',
        'core.change_user', 'core.view_user'
    )

    def get_permission_required(self):
        perms = super().get_permission_required()
        staff_id = self.request.GET.get('staff-id', '')

        # if a user is attempting to view their own staff info, then they can be allowed to do so
        if staff_id and staff_id.isdigit() and int(staff_id) == self.request.user.pk:
            perms = tuple()
        return perms

    def staff_member_permissions(self, all_permissions: Set[str], staff_pk: int) -> List[str]:
        perms = []
        prefix = 'You can' if self.request.user.pk == staff_pk else 'Can'

        for perm in all_permissions:
            perm_ = perm.split('.')
            perm_ = perm_[-1] if len(perm_) == 2 else ''
            if perm_:
                perm_ = perm_.translate(str.maketrans('_', ' '))

                perms.append(
                    f'{prefix} {perm_}'
                )

        return perms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_id = self.request.GET.get('staff-id', '')
        staff = User.objects.filter(is_staff=True)

        if staff_id and staff_id.isdigit():
            try:
                staff_member: User = staff.get(pk=int(staff_id))
                perms = self.staff_member_permissions(staff_member.get_all_permissions(), staff_member.pk)
            except ObjectDoesNotExist:
                staff_member = None
                perms = []
            context.update({
                'staff_member': staff_member,
                'staff_id': staff_id,
                'staff_member_permissions': perms
            })

        else:
            query = self.request.GET.get('q', '')
            if query:
                staff = staff.filter((Q(username__icontains=query) | Q(email__icontains=query)))

            context.update({
                'staff': staff,
                'q': query if query else None
            })
        return context


class StaffLogs(StaffAccessMixin, generic.TemplateView):
    template_name = 'staff/staff_logs.html'

    # only superusers can access this page
    def test_func(self):
        if hasattr(self.request.user, 'is_superuser'):
            return self.request.user.is_superuser
