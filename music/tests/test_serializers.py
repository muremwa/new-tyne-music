from django.test import TestCase, tag

from core.models import User
from music import serializers as m_serializers
from music.models import Artist, Genre, Song, Album, Disc, LibraryAlbum, Playlist, Creator, CreatorSection


@tag('music-s-artist')
class ArtistSerializerTestCase(TestCase):
    def setUp(self):
        self.artist_1: Artist = Artist.objects.create(
            name='Quavo',
        )
        self.artist_2: Artist = Artist.objects.create(
            name='Takeoff'
        )
        self.artist_3: Artist = Artist.objects.create(
            name='Offset'
        )
        self.artist_4: Artist = Artist.objects.create(
            name='Migos',
            is_group=True
        )
        for artist in [self.artist_1, self.artist_2, self.artist_3]:
            self.artist_4.add_artist_to_group(artist)

    def test_one_data(self):
        ase = m_serializers.ArtistSerializer(self.artist_1)
        data = {
            'name': self.artist_1.name,
            'is_group': False,
            'group_members': None,
            'avi': '/media/defaults/artist.png',
            'cover': '/media/defaults/artist_large.png',
            'bio': None,
            'id': self.artist_1.pk
        }
        self.assertDictEqual(ase.data, data)

    def test_grp_data(self):
        ase = m_serializers.ArtistSerializer(self.artist_4)
        members = m_serializers.ArtistSerializer(self.artist_4.group_members.all(), many=True)
        self.assertEqual(ase.data.get('group_members'), members.data)


@tag('music-s-genre')
class GenreSerializerTestCase(TestCase):
    def test_genres(self):
        genre = Genre.objects.create(
            title='Pop'
        )
        self.assertDictEqual(
            m_serializers.GenreSerializer(genre).data,
            {
                'title': 'Pop',
                'description': '',
                'avi': '/media/defaults/genre.png',
                'cover': '/media/defaults/genre_wide.png',
                'id': genre.pk
            }
        )


@tag('music-s-x')
class MusicSerializerTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.genre: Genre = Genre.objects.create(
            title='Hip-Hop'
        )
        self.genre_2: Genre = Genre.objects.create(
            title='R&B'
        )
        self.artist_1: Artist = Artist.objects.create(
            name='Quavo',
        )
        self.artist_2: Artist = Artist.objects.create(
            name='Takeoff'
        )
        self.album_1: Album = Album.objects.create(
            title='WAX',
            genre=self.genre,
            date_of_release='2021-05-05'
        )
        self.album_1.artists.add(self.artist_1)
        self.song_1: Song = Song.objects.create(
            title='Timmy',
            track_no=1,
            disc=self.album_1.disc_one,
            genre=self.genre,
            length=285
        )
        self.song_1.add_additional_artist(self.artist_2)
        self.disc_2 = Disc.objects.create(
            name='Disc 2',
            album=self.album_1
        )
        self.song_2: Song = Song.objects.create(
            title='Timmy Block 2',
            track_no=1,
            disc=self.disc_2,
            genre=self.genre,
            length=585
        )
        self.album_2: Album = Album.objects.create(
            title='WAX (Deluxe)',
            genre=self.genre,
            date_of_release='2021-05-12'
        )
        self.album_2.artists.add(self.artist_1)
        self.album_2.add_sister_album(self.album_1)
        self.song_3 = Song.objects.create(
            title='Pig',
            track_no=3,
            disc=self.album_1.disc_one,
            genre=self.genre,
            length=265
        )
        self.song_4 = Song.objects.create(
            title='Pig',
            track_no=3,
            disc=self.album_2.disc_one,
            genre=self.genre,
            length=265
        )
        self.creator: Creator = Creator.objects.create(
            name='Tyne Music Pop'
        )
        self.section: CreatorSection = CreatorSection.objects.create(
            name='Favourites',
            creator=self.creator
        )
        self.playlist_1: Playlist = Playlist.objects.create(
            title='All Time Pop',
            creator=self.creator
        )
        self.user = User.objects.create_user(
            username='pl',
            email='pl@tyne.com',
            password='pass@123',
            is_staff=True
        )
        self.creator.add_creator_user(self.user)
        self.playlist_2: Playlist = Playlist.objects.create(
            title='Home work',
            profile=self.user.main_profile
        )

        for g in Genre.objects.all():
            self.creator.genres.add(g)

        for artist in Artist.objects.all():
            self.section.artists.add(artist)

        for album in Album.objects.all():
            self.section.albums.add(album)

        for pl in Playlist.objects.all():
            self.section.playlists.add(pl)

        for song in [self.song_1, self.song_2, self.song_3]:
            self.playlist_1.add_song_to_playlist(song)
            self.playlist_2.add_song_to_playlist(song, 0)

        self.lib_album: LibraryAlbum = LibraryAlbum.objects.create(
            profile=self.user.main_profile,
            album=self.album_1
        )

        for song in self.album_1.all_songs():
            self.lib_album.songs.add(song)

        self.lib_album_2: LibraryAlbum = LibraryAlbum.objects.create(
            profile=self.user.main_profile,
            album=self.album_2
        )
        for song in self.album_2.all_songs():
            self.lib_album.songs.add(song)

    def test_song_data(self):
        ss = m_serializers.SongSerializer(self.song_1)
        self.assertDictEqual(
            ss.data,
            {
                'id': self.song_1.pk,
                'track_no': self.song_1.track_no,
                'title': self.song_1.title,
                'explicit': self.song_1.explicit,
                'length': self.song_1.length,
                'file': None,
                'likes': 0,
                'streams': 0,
                'additional_artists': m_serializers.ArtistSerializer(
                    self.song_1.additional_artists.all(), many=True
                ).data
            }
        )

    def test_disc_data(self):
        disc = self.album_1.disc_one
        ds = m_serializers.DiscSerializer(disc)
        self.assertDictEqual(
            ds.data,
            {
                'id': disc.pk,
                'name': disc.name,
                'songs': m_serializers.SongSerializer(disc.song_set.all(), many=True).data
            }
        )

    def test_album_data(self):
        ase = m_serializers.AlbumSerializer(self.album_1)
        data = {
            'id': self.album_1.pk,
            'title': self.album_1.title,
            'notes': self.album_1.notes,
            'genre': m_serializers.GenreSerializer(self.album_1.genre).data,
            'date_of_release': str(self.album_1.date_of_release),
            'album_type': self.album_1.al_code(),
            'cover': '/media/defaults/album.png',
            'likes': 0,
            'artists': m_serializers.ArtistSerializer(self.album_1.artists.all(), many=True, read_only=True).data,
            'copyright': self.album_1.copyright,
            'published': self.album_1.published,
            'discs': m_serializers.DiscSerializer(self.album_1.disc_set.all(), many=True, read_only=True).data
        }
        self.assertDictEqual(ase.data, data)
        ase = m_serializers.AlbumSerializer(self.album_1, no_discs=True)
        data.pop('discs')
        self.assertDictEqual(ase.data, data)

    def test_playlist(self):
        ps = m_serializers.PlaylistSerializer(self.playlist_1)
        self.assertDictEqual(
            ps.data,
            {
                'id': self.playlist_1.pk,
                'title': self.playlist_1.title,
                'description': None,
                'owner': self.playlist_1.owner(),
                'songs': m_serializers.SongSerializer(self.playlist_1.songs_by_order(), many=True, read_only=True).data,
                'likes': 0,
                'cover': '/media/defaults/playlist.png',
                'cover_wide': '/media/defaults/playlist_wide.png',
                'timely_cover': None,
                'timely_cover_wide': None,
                'modified': self.playlist_1.modified.strftime('%Y-%m-%d')
            }
        )

    def test_creator_section_data(self):
        cs = m_serializers.CreatorSectionSerializer(self.section)
        self.assertDictEqual(
            cs.data,
            {
                'id': self.section.pk,
                'name': self.section.name,
                'artists': m_serializers.ArtistSerializer(
                    self.section.artists.all(),
                    many=True,
                    read_only=True
                ).data,
                'albums': m_serializers.AlbumSerializer(
                    self.section.albums.all(),
                    many=True,
                    read_only=True
                ).data,
                'playlists': m_serializers.PlaylistSerializer(
                    self.section.playlists.all(),
                    many=True,
                    read_only=True
                ).data
            }
        )

    def test_creator_data(self):
        cs = m_serializers.CreatorSerializer(self.creator)
        self.assertDictEqual(
            cs.data,
            {
                'id': self.creator.pk,
                'name': self.creator.name,
                'description': None,
                'avi': '/media/defaults/creator.png',
                'cover': '/media/defaults/creator_wide.png',
                'users': m_serializers.UserSerializer(self.creator.users.all(), many=True, read_only=True).data,
                'genres': m_serializers.GenreSerializer(self.creator.genres.all(), many=True, read_only=True).data
            }
        )

    def test_library_album_data(self):
        las = m_serializers.LibraryAlbumSerializer(self.lib_album)
        self.assertDictEqual(las.data, {
            'id': self.lib_album.pk,
            'added': self.lib_album.added.strftime('%Y-%m-%d'),
            'modified': self.lib_album.modified.strftime('%Y-%m-%d'),
            'album': m_serializers.AlbumSerializer(self.lib_album.album, no_discs=True, read_only=True).data,
            'songs': m_serializers.SongSerializer(self.lib_album.songs.all(), many=True, read_only=True).data
        })
