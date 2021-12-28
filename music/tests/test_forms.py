from django.test import TestCase, tag

from core.models import User
from music import forms
from music import models as music_models


@tag('music-f')
class MusicFormsTestCase(TestCase):
    def setUp(self):
        self.genre = music_models.Genre.objects.create(
            title='Hip-hop'
        )
        self.album = music_models.Album.objects.create(
            title='B',
            date_of_release='2021-02-10',
            genre=self.genre
        )

    @tag('music-f-a')
    def test_artist_form(self):
        form = forms.ArtistForm(data={
            'name': 'Quavo',
            'bio': 'Best rapper ever'
        })

        if form.is_valid():
            artist: music_models.Artist = form.save()
            self.assertEqual(artist.name, 'Quavo')
            self.assertEqual(artist.bio, 'Best rapper ever')

        self.assertEqual(music_models.Artist.objects.filter(name__icontains='Quavo').count(), 1)

        # edit artist
        artist = music_models.Artist.objects.get(name='Quavo')
        new_bio = 'What a time to be alive'
        # no instance
        form = forms.ArtistEditForm(data={
            'bio': new_bio
        })
        self.assertFalse(form.is_valid())

        # instance exists
        form = forms.ArtistEditForm(data={
            'bio': new_bio
        }, instance=artist)
        self.assertTrue(form.is_valid())

        if form.is_valid():
            form.save()
            artist.refresh_from_db()
            self.assertEqual(artist.bio, new_bio)

    def test_album_form(self):
        form = forms.AlbumForm(data={
            'title': 'Silent Auction',
            'date_of_release': '2020-05-05',
            'genre': self.genre.pk
        })
        self.assertTrue(form.is_valid())

        if form.is_valid():
            album: music_models.Album = form.save()
            self.assertEqual(album.title, 'Silent Auction')
            self.assertEqual(album.cover.url, '/media/defaults/album.png')
            self.assertEqual(album.disc_one.name, 'Disc 1')

        self.assertEqual(music_models.Album.objects.filter(title__icontains='Silent Auction').count(), 1)
        self.assertEqual(music_models.Disc.objects.filter(album__title__icontains='Silent Auction').count(), 1)

        # edit album form
        form = forms.AlbumEditForm({
            'date_of_release': '2021-05-30'
        })
        self.assertFalse(form.is_valid())

        # with instance
        album = music_models.Album.objects.get(title='Silent Auction')
        form = forms.AlbumEditForm({
            'date_of_release': '2021-05-30'
        }, instance=album)

        self.assertTrue(form.is_valid())

        if form.is_valid():
            form.save()
            album.refresh_from_db()
            self.assertEqual(str(album.date_of_release), '2021-05-30')

    def test_genre_form(self):
        form = forms.GenreForm(data={
            'title': 'R&B',
            'description': 'Description example'
        })
        self.assertTrue(form.is_valid())

        if form.is_valid():
            genre = form.save()
            self.assertEqual(genre.title, 'R&B')

        self.assertEqual(music_models.Genre.objects.filter(title__icontains='R&B').count(), 1)

        # edit form
        form = forms.GenreEditForm({
            'description': 'NEW'
        }, instance=self.genre)
        self.assertTrue(form.is_valid())

        if form.is_valid():
            form.save()
            self.genre.refresh_from_db()
            self.assertEqual(self.genre.description, 'NEW')

    def test_disc_form(self):
        form = forms.DiscForm(data={
            'name': 'Disc 2',
            'album': self.album.pk
        })
        self.assertTrue(form.is_valid())

        if form.is_valid():
            disc = form.save()
            self.assertEqual(disc.name, 'Disc 2')
            self.assertEqual(disc.album, self.album)

        self.assertEqual(self.album.disc_set.count(), 2)

        # edit
        disc = self.album.disc_set.get(name='Disc 2')
        form = forms.DiscEditForm({
            'name': 'Disc Two'
        }, instance=disc)
        self.assertTrue(form.is_valid())

        if form.is_valid():
            form.save()
            disc.refresh_from_db()
            self.assertEqual(disc.name, 'Disc Two')

    @tag('music-f-sf')
    def test_song_form(self):
        form = forms.SongForm(data={
            'track_no': 1,
            'title': 'BRUCE.',
            'genre': self.genre.pk,
            'explicit': False,
        }, song_disc=self.album.disc_one)

        self.assertTrue(form.is_valid())

        if form.is_valid():
            song = form.save(commit=False)
            song.disc = self.album.disc_one
            song.save()
            self.assertEqual(song.title, 'BRUCE.')

        self.assertEqual(len(self.album.all_songs()), 1)

        # edit
        song = self.album.all_songs()[0]
        form = forms.SongEditForm({
            'explicit': True
        }, instance=song)
        self.assertTrue(form.is_valid())

        if form.is_valid():
            form.save()
            song.refresh_from_db()
            self.assertTrue(song.explicit)

    def test_creator_and_section_form(self):
        c_form = forms.CreatorForm(data={
            'name': 'Tyne Music',
        })
        self.assertTrue(c_form.is_valid())

        if c_form.is_valid():
            creator = c_form.save()
            self.assertEqual(creator.name, 'Tyne Music')

        creator = music_models.Creator.objects.get(name='Tyne Music')

        # edit creator
        c_form = forms.CreatorEditForm({
            'name': 'Tyne Music Access'
        }, instance=creator)
        self.assertTrue(c_form.is_valid())

        if c_form.is_valid():
            c_form.save()
            creator.refresh_from_db()
        self.assertEqual(creator.name, 'Tyne Music Access')

        # section
        cs_form = forms.CreatorSectionForm(data={
            'name': 'Top albums',
            'creator': creator.pk
        })
        self.assertTrue(cs_form.is_valid())

        if cs_form.is_valid():
            cs = cs_form.save()
            self.assertEqual(cs.name, 'Top albums')
            self.assertEqual(cs.creator, creator)

        self.assertEqual(creator.creatorsection_set.count(), 1)

        # edit
        cs: music_models.CreatorSection = creator.creatorsection_set.all()[0]
        cs_form = forms.CreatorSectionEditForm({
            'name': 'Top Artists',
        }, instance=cs)
        self.assertTrue(cs_form.is_valid())

        if cs_form.is_valid():
            cs_form.save()
            cs.refresh_from_db()
            self.assertEqual(cs.name, 'Top Artists')

    def test_profile_playlist_form(self):
        user = User.objects.create_user(
            username='user',
            email='user@tyne.com',
            password='pass@123'
        )
        pl_form = forms.ProfilePlaylistForm(data={
            'title': 'WAX',
            'profile': user.main_profile.pk
        })
        self.assertTrue(pl_form.is_valid())

        if pl_form.is_valid():
            pl: music_models.Playlist = pl_form.save()
            self.assertEqual(pl.title, 'WAX')
            self.assertEqual(pl.owner(), user.main_profile.name)

        # edit form
        pl = user.main_profile.playlist_set.get(title__exact='WAX')
        pl_form = forms.ProfilePlaylistEditForm({
            'title': 'WEST'
        }, instance=pl)
        self.assertTrue(pl_form.is_valid())

        if pl_form.is_valid():
            pl_form.save()
            pl.refresh_from_db()
            self.assertEqual(pl.title, 'WEST')

    def test_creator_playlist_form(self):
        creator = music_models.Creator.objects.create(name='Tyne Music')
        pl_form = forms.CreatorPlaylistForm(data={
            'title': 'Top R&B songs',
            'creator': creator.pk
        })
        self.assertTrue(pl_form.is_valid())

        if pl_form.is_valid():
            pl: music_models.Playlist = pl_form.save()
            self.assertEqual(pl.title, 'Top R&B songs')
            self.assertEqual(pl.owner(), creator.name)

        # edit form
        pl = creator.playlist_set.get(title__exact='Top R&B songs')
        pl_form = forms.ProfilePlaylistEditForm({
            'description': 'Top R&B from songs 2011'
        }, instance=pl)
        self.assertTrue(pl_form.is_valid())

        if pl_form.is_valid():
            pl_form.save()
            pl.refresh_from_db()
            self.assertEqual(pl.description, 'Top R&B from songs 2011')
