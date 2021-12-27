from typing import List, Set
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View, generic
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.http import Http404, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.messages import add_message, constants as message_constants

import mutagen

from core.models import User
from music.models import Album, Artist, Disc, Song
from music.forms import AlbumEditForm, AlbumForm, ArtistEditForm, ArtistForm, SongEditForm, SongForm
from tyne_utils.funcs import is_string_true_or_false, strip_punctuation
from .models import HelpArticle
from .forms import HelpArticleForm, HelpArticleEditForm, LogSearchForm
from .logs_processing import log_action_ids, staff_logs
from .staff_actions import staff_actions, superuser_actions


staff_logger = logging.getLogger('tyne.staff')


def info_log_staff_message(action_id: log_action_ids, message: str):
    staff_logger.info(f'ID: {action_id}:{message}')


@user_passes_test(test_func=lambda user: user.is_staff)
def artists_names(request):
    if request.method == 'GET':
        name = request.GET.get('name', '')
        artists = Artist.objects.filter(name__icontains=name)
        return JsonResponse([[artist.name, artist.pk] for artist in artists], safe=False)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_actions = [action for action in staff_actions if self.request.user.has_perms(action.get('permissions', []))]

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
        return reverse('staff:help-article', kwargs={'article_pk': str(self.object.pk)})


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
        return reverse('staff:help-article', kwargs={'article_pk': str(self.object.pk)})


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


class StaffAlbumView(StaffAccessMixin, StaffPermissionMixin, generic.TemplateView):
    template_name = 'staff/albums.html'
    permission_required = (
        'music.add_album', 'music.view_album', 'music.change_album', 'music.delete_album'
    )

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
            albums = Album.objects.order_by('title')

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
        'music.view_album', 'music.change_album',
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


class AlbumEditingAbstract(StaffAccessMixin, StaffPermissionMixin, generic.FormView):
    new_album = False

    @staticmethod
    def retrieve_artist(artist_id):
        try:
            artist = Artist.objects.get(pk=artist_id)
            return artist
        except ObjectDoesNotExist:
            return None

    def log_activity(self, pk, title):
        if self.new_album:
            done_action = 'created'
            done_action_id = log_action_ids.CREATE_ALBUM
        else:
            done_action = 'edited'
            done_action_id = log_action_ids.EDIT_ALBUM

        user = f'{self.request.user.username}({self.request.user.pk})'
        message = f'{user} {done_action} album {title}({pk})'
        info_log_staff_message(done_action_id, message)

    def form_valid(self, form):
        is_single = self.request.POST.get('is_single')
        is_ep = self.request.POST.get('is_ep')
        album = form.save(commit=False)
        artists = self.request.POST.get('album-artists')

        if is_single:
            album.is_single = True
            album.is_ep = False

        elif is_ep:
            album.is_ep = True
            album.is_single = False

        else:
            album.is_single = False
            album.is_ep = False

        album.save()

        if artists:
            artists = [int(artist_id) for artist_id in artists.split(',')]
            artists_objs = [self.retrieve_artist(artist_id) for artist_id in artists]
            album.artists.clear()
            album.artists.add(*[artist for artist in artists_objs if artist])

        self.log_activity(album.pk, album.title)

        return redirect(f'{reverse("staff:manage-albums")}?album-id={album.pk}')

    def form_invalid(self, form):
        return render(self.request, self.template_name, {
            'form': form
        })


# edit an album
class AlbumEditView(AlbumEditingAbstract):
    form_class = AlbumEditForm
    template_name = 'staff/edit_album.html'
    permission_required = (
        'music.view_album', 'music.change_album',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['album'] = get_object_or_404(Album, pk=self.kwargs.get('album_pk'))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        album = get_object_or_404(Album, pk=self.kwargs.get('album_pk'))
        kwargs['instance'] = album

        if self.request.method == 'GET':
            kwargs['initial'] = {
                key: getattr(album, key) for key in self.form_class().fields_info()
            }
        return kwargs


class StaffAlbumCreateView(AlbumEditingAbstract):
    new_album = True
    form_class = AlbumForm
    template_name = 'staff/create_album.html'
    permission_required = (
        'music.add_album', 'music.view_album',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist_pks = self.request.GET.get('artists')

        if artist_pks:
            artist_pks = set([int(pk) for pk in artist_pks.split(',') if pk.strip().isdigit()])
            artist_pks = [pk for pk in artist_pks if pk > -1]
            context['force_artists'] = Artist.objects.filter(pk__in=artist_pks)

        return context


class AlbumDelete(StaffAccessMixin, StaffPermissionMixin, generic.DeleteView):
    model = Album
    pk_url_kwarg = 'album_pk'
    context_object_name = 'album'
    permission_required = ('music.delete_album', 'music.change_album')
    template_name = 'staff/album_confirm_delete.html'

    def get_success_url(self):
        album = f'{strip_punctuation(self.object.title)}({self.object.pk})'
        m = f'{self.request.user.username}({self.request.user.pk}) deleted album {album}'
        info_log_staff_message(log_action_ids.DELETE_ALBUM, m)
        return reverse('staff:manage-albums')


class StaffArtistsView(StaffAccessMixin, StaffPermissionMixin, generic.TemplateView):
    template_name = 'staff/artists/manage_artists.html'
    permission_required = (
        'music.view_artist', 'music.add_artist', 'music.change_artist', 'music.delete_artist'
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artist_id = self.request.GET.get('artist-id')

        if artist_id and artist_id.strip().isdigit():
            artist_id = int(artist_id)
            context.update({
                'artist_id': artist_id,
                'artist': get_object_or_404(Artist, pk=artist_id)
            })

        else:
            query = self.request.GET.get('q')
            artist_type = self.request.GET.get('t')
            artists = Artist.objects.order_by('name')

            if artist_type and artist_type in ['G', 'L']:
                group_status = True if artist_type == 'G' else False
                artists = artists.filter(is_group=group_status)
                context['artist_type'] = artist_type

            if query:
                artists = artists.filter((Q(name__icontains=query) | Q(nicknames__icontains=query)))
                context['q'] = query

            context['artists'] = artists

        return context


class EditArtistGroupMember(StaffAccessMixin, StaffPermissionMixin, View):
    permission_required = (
        'music.view_artist', 'music.change_artist'
    )

    def log_action(self, artist):
        m = f'{self.request.user.username}({self.request.user.pk}) edited {artist}'
        info_log_staff_message(log_action_ids.EDIT_ARTIST, m)

    def post(self, request, **kwargs):
        artist = get_object_or_404(Artist, pk=kwargs.get('artist_id'))

        if not artist.is_group:
            raise Http404

        artists = request.POST.get('group-artists')

        if artists:
            grp_artists = {int(artist_id) for artist_id in artists.split(',')}
            artists = Artist.objects.filter(pk__in=grp_artists, is_group=False)
            artist.group_members.clear()

            for member in artists:
                artist.add_artist_to_group(member)

            self.log_action(f'{artist.name}({artist.pk})')

        return redirect(f"{reverse('staff:manage-artists')}?artist-id={artist.pk}#group-members-edit")


class EditArtistAbstract(StaffAccessMixin, StaffPermissionMixin, generic.FormView):
    form_class = ArtistEditForm
    new_artist = False

    def log_action(self, artist: Artist):
        user = f'{self.request.user.username}({self.request.user.pk})'
        artist = f'{artist.name}({artist.pk})'
        action = 'created' if self.new_artist else 'edited'
        info_log_staff_message(log_action_ids.EDIT_ARTIST, f'{user} {action} artist {artist}')

    def form_valid(self, form: ArtistEditForm):
        artist = form.save()
        self.log_action(artist)
        return redirect(f"{reverse('staff:manage-artists')}?artist-id={artist.pk}")

    def form_invalid(self, form):
        artist = get_object_or_404(Artist, pk=self.kwargs.get('artist_id')) if self.kwargs.get('artist_id') else None

        return render(self.request, self.template_name, {
            'form': form,
            'artist': artist
        })


class EditArtist(EditArtistAbstract):
    template_name = 'staff/artists/edit_artist.html'
    permission_required = (
        'music.view_artist', 'music.change_artist'
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['artist'] = get_object_or_404(Artist, pk=self.kwargs.get('artist_id'))
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        artist = get_object_or_404(Artist, pk=self.kwargs.get('artist_id'))
        kwargs['instance'] = artist

        if self.request.method == 'GET':
            kwargs['initial'] = {
                key: getattr(artist, key) for key in self.form_class().fields_info()
            }
        return kwargs


class ArtistCreate(EditArtistAbstract):
    new_artist = True
    template_name = 'staff/artists/create_artist.html'
    form_class = ArtistForm
    permission_required = (
        'music.view_artist', 'music.add_artist'
    )


class ArtistDelete(StaffAccessMixin, StaffPermissionMixin, generic.DeleteView):
    model = Artist
    template_name = 'staff/artists/artist_delete.html'
    pk_url_kwarg = 'artist_id'
    context_object_name = 'artist'
    permission_required = (
        'music.view_artist', 'music.delete_artist'
    )

    def get_success_url(self):
        user = f'{self.request.user.username}({self.request.user.pk})'
        artist = f'{self.object.name}({self.object.pk})'
        info_log_staff_message(log_action_ids.DELETE_ARTIST, f'{user} deleted artist {artist}')
        return reverse('staff:manage-artists')


# add a disc to an album
@user_passes_test(test_func=lambda user: user.is_staff)
def add_disc_to_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    disc_pk = 0

    if request.method == 'POST':
        disc = Disc.objects.create(
            name=f'Disc {album.disc_set.count() + 1}',
            album=album
        )
        disc_pk = disc.pk

    return redirect(f"{reverse('staff:manage-albums')}?album-id={album.pk}#disc-{disc_pk}")


# delete a disc from album
@user_passes_test(test_func=lambda user: user.is_staff)
def delete_disc_from_album(request, disc_id):
    disc = get_object_or_404(Disc, pk=disc_id)

    if request.method == 'POST' and disc.song_set.count() == 0 and disc.album.disc_set.count() > 1:
        disc.delete()

    return redirect(f"{reverse('staff:manage-albums')}?album-id={disc.album.pk}")


# change disc name
@user_passes_test(test_func=lambda user: user.is_staff)
def change_disc_name(request, disc_id):
    disc = get_object_or_404(Disc, pk=disc_id)

    if request.method == 'POST':
        new_name = request.POST.get('disc-name')

        if new_name:
            disc.name = new_name
            disc.save()

    return redirect(f"{reverse('staff:manage-albums')}?album-id={disc.album.pk}#disc-{disc.pk}")


# abstract for song
class SongAbstract(StaffAccessMixin, StaffPermissionMixin, generic.FormView):
    def form_invalid(self, form):
        return render(self.request, self.template_name, {
            'form': form
        })

    def extra_steps(self, song):
        # length of song
        song_file = self.request.FILES.get('file')

        if song_file:
            song_file_x = mutagen.File(song_file)
            song.length = song_file_x.info.length

        if not song.pk:
            song.save()

        # edit featured artists
        feat_artists = self.request.POST.get('featured-artists', '')
        if feat_artists:
            feat_artists = [int(ar_pk) for ar_pk in feat_artists.split(',')]
            feat_artists = Artist.objects.filter(pk__in=feat_artists)
            song.featured_artists.clear()

            for artist in feat_artists:
                song.add_featured_artist(artist)

        # additional artists
        add_artists = self.request.POST.get('additional-artists', '')
        if add_artists:
            add_artists = [int(ar_pk) for ar_pk in add_artists.split(',')]
            add_artists = Artist.objects.filter(pk__in=add_artists)
            song.additional_artists.clear()

            for artist in add_artists:
                song.add_additional_artist(artist)


# edit song
class EditSongView(SongAbstract):
    form_class = SongEditForm
    template_name = 'staff/albums/songs/edit_song.html'
    permission_required = (
        'music.view_song', 'music.change_song', 'music.delete_song'
    )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        song = get_object_or_404(Song, pk=self.kwargs.get('song_id'))
        kwargs['instance'] = song

        if self.request.method == 'GET':
            kwargs['initial'] = {
                key: getattr(song, key) for key in self.form_class().fields_info()
            }
        return kwargs

    def form_valid(self, form):
        song = form.instance
        self.extra_steps(song)
        form.save()
        return redirect(f"{reverse('staff:manage-albums')}?album-id={song.disc.album.pk}#disc-{song.disc.pk}")


# create a new song
class CreateSongView(SongAbstract):
    form_class = SongForm
    template_name = 'staff/albums/songs/create_song.html'
    permission_required = (
        'music.view_song', 'music.change_song', 'music.delete_song'
    )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['song_disc'] = get_object_or_404(Disc, pk=self.kwargs.get('disc_id'))
        return kwargs

    def form_valid(self, form):
        song = form.save(commit=False)
        disc = get_object_or_404(Disc, pk=self.kwargs.get('disc_id'))
        song.disc = disc
        self.extra_steps(song)
        return redirect(f"{reverse('staff:manage-albums')}?album-id={song.disc.album.pk}#disc-{song.disc.pk}")


# delete a song
class DeleteSongView(StaffAccessMixin, StaffPermissionMixin, generic.DeleteView):
    model = Song
    pk_url_kwarg = 'song_id'
    context_object_name = 'song'
    template_name = 'staff/albums/songs/delete_song.html'
    permission_required = (
        'music.delete_song', 'music.view_song'
    )

    def get_success_url(self):
        user = f'{self.request.user.username}({self.request.user.pk})'
        song = f'{self.object.title}({self.object.pk})'
        info_log_staff_message(log_action_ids.DELETE_SONG, f'{user} deleted song {song}')
        return f"{reverse('staff:manage-albums')}?album-id={self.object.disc.album.pk}#disc-{self.object.disc.pk}"
