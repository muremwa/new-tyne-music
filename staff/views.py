from typing import List, Set
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View, generic
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.messages import add_message, constants as message_constants

from core.models import User
from music.models import Album
from tyne_utils.funcs import is_string_true_or_false, strip_punctuation
from .models import HelpArticle
from .forms import HelpArticleForm, HelpArticleEditForm, LogSearchForm
from .logs_processing import log_action_ids, staff_logs
from .staff_actions import staff_actions, superuser_actions


staff_logger = logging.getLogger('tyne.staff')


def info_log_staff_message(action_id, message):
    staff_logger.info(f'ID: {action_id}:{message}')


# access mixin for staff, throw 404 if user not staff or superuser denied
class StaffAccessMixin(UserPassesTestMixin):
    def test_func(self):
        if hasattr(self, 'request'):
            return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        raise Http404


# superuser access mixin
class SuperuserAccessMixin(StaffAccessMixin):
    # only superusers can access this page
    def test_func(self):
        if hasattr(self, 'request') and hasattr(self.request.user, 'is_superuser'):
            return self.request.user.is_superuser


# permission mixin for staff, throw 404 if permission denied
class StaffPermissionMixin(PermissionRequiredMixin):
    def handle_no_permission(self):
        raise Http404


# see all user available actions
class StaffHome(StaffAccessMixin, generic.TemplateView):
    template_name = 'staff/staff_home.html'

    def include_action(self, action_perms: List[str]) -> bool:
        return all([self.request.user.has_perm(perm) for perm in action_perms])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_actions = [action for action in staff_actions if self.include_action(action.get('permissions'))]

        if self.request.user.is_superuser:
            all_actions.extend(superuser_actions)

        context.update({
            'staff_actions': all_actions
        })
        return context


# manage a user, give a user permission
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
                f'{self.log_message_user()}) added {user_info} to {strip_punctuation(group.name)}'
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


# view help articles listed
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


# view a help article
class StaffHelpArticlePage(StaffAccessMixin, generic.DetailView):
    queryset = HelpArticle.objects.all()
    pk_url_kwarg = 'article_pk'
    context_object_name = 'article'
    template_name = 'staff/help_detail.html'


# add a help article
class StaffArticleAdd(StaffAccessMixin, PermissionRequiredMixin, generic.CreateView):
    model = HelpArticle
    form_class = HelpArticleForm
    template_name = 'staff/article_edit.html'
    permission_required = ('staff.add_helparticle',)

    def get_success_url(self):
        user_info = f'{self.request.user.username}({self.request.user.pk})'
        info_log_staff_message(
            log_action_ids.CREATE_ARTICLE,
            f'{user_info} created article {strip_punctuation(self.object.title)}({self.object.pk})'
        )
        return reverse("staff:help-article", kwargs={"article_slug": str(self.object.slug)})


# edit a help article
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
            f'{user_info} edited article {strip_punctuation(self.object.title)}({self.object.pk})'
        )
        return reverse("staff:help-article", kwargs={"article_slug": str(self.object.slug)})


# edit a help article
class StaffArticleHelpDelete(StaffAccessMixin, PermissionRequiredMixin, generic.DeleteView):
    model = HelpArticle
    pk_url_kwarg = 'article_pk'
    context_object_name = 'article'
    permission_required = ('staff.delete_helparticle',)

    def get_success_url(self):
        user_info = f'{self.request.user.username}({self.request.user.pk})'
        info_log_staff_message(
            log_action_ids.DELETE_ARTICLE,
            f'{user_info} deleted article {strip_punctuation(self.object.title)}({self.object.pk})'
        )
        return reverse("staff:help-list")


# view users and their roles
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


# view groups and their users
class GroupInfoView(SuperuserAccessMixin, generic.TemplateView):
    template_name = 'staff/groups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        group_id = self.request.GET.get('group-id', '')

        if group_id and group_id.isdigit():
            context.update({
                'group': get_object_or_404(Group, pk=int(group_id)),
                'group_id': group_id
            })

        return context


# view staff activity
class StaffLogs(SuperuserAccessMixin, generic.TemplateView):
    template_name = 'staff/staff_logs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_form = LogSearchForm(self.request.GET)
        q = self.request.GET.get('q', '')
        filtered = False

        if q:
            log_form = LogSearchForm({
                'user': q
            })

        if log_form.is_valid() and log_form.has_changed():
            logs = list(reversed(log_form.get_logs()))
            filtered = True
        else:
            logs = list(reversed(staff_logs.get_logs()))

            if not self.request.GET.get('all'):
                logs = logs[:20]

        context.update({
            'log_form': log_form,
            'show_help': self.request.GET.get('h'),
            'logs': logs,
            'filtered': filtered,
            'q': q
        })
        return context


class StaffAlbumView(StaffAccessMixin, generic.TemplateView):
    template_name = 'staff/albums.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        album_id = self.request.GET.get('album-id', '')

        if album_id and album_id.isdigit():
            context.update({
                'album': get_object_or_404(Album, pk=int(album_id)),
                'album_id': album_id
            })
        else:
            album_type = self.request.GET.get('t', '')
            query = self.request.GET.get('q', '')
            albums = Album.objects.all()

            if album_type and album_type in ('EP', 'LP', 'S'):
                if album_type == 'EP':
                    albums = albums.filter(is_ep=True)
                elif album_type == 'S':
                    albums = albums.filter(is_single=True)
                elif album_type == 'LP':
                    albums = albums.filter(is_ep=False, is_single=False)

            if query:
                albums = albums.filter((
                    Q(title__icontains=query) |
                    Q(artists__name__icontains=query) |
                    Q(artists__group_members__name__icontains=query, artists__is_group=True)
                )).order_by('-date_of_release')

            context.update({
                'albums': albums,
                'q': query,
                'album_type': album_type
            })
        return context


class PublishAlbums(StaffAccessMixin, StaffPermissionMixin, View):
    permission_required = (
        'music.change_album'
    )

    def log_message(self, album: Album, action: bool=True):
        message = 'published' if action else 'un published'
        title = strip_punctuation(album.title)
        info_log_staff_message(
            log_action_ids.PUBLISH_ALBUM if action else log_action_ids.UN_PUBLISH_ALBUM,
            f'{self.request.user.username}({self.request.user.pk}) {message} {title}({album.pk})'
        )

    def post(self, request, **kwargs):
        album = get_object_or_404(Album, pk=kwargs.get('album_pk'))

        # publish
        publish = request.POST.get('publish')
        if publish and not album.published:
            album.published = True
            album.save()
            self.log_message(album)

        # un publish
        un_publish = request.POST.get('un-publish')
        if un_publish and album.published:
            album.published = False
            album.save()
            self.log_message(album, False)

        return redirect(f'{reverse("staff:manage-albums")}?album-id={album.pk}')
