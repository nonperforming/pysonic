"""Fields for OpenSubsonic responses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from json import loads as deserialize_json
from re import compile as regex_compile
from typing import Annotated, Any, Literal, Self, get_args, get_origin


# Typing
@dataclass
class ValueRange:
    """Represents the range of values a number can have."""

    min: float | int | None
    """Minimum value."""
    max: float | int | None
    """Maximum value."""


# Internal workings
_camel_case_to_snake_case_pattern = regex_compile(r"(?<!^)(?=[A-Z])")


def _camel_to_snake_case(camel_case: str) -> str:
    camel_case.replace("musicBrainz", "musicbrainz")
    return _camel_case_to_snake_case_pattern.sub("_", camel_case).lower()


def _snake_to_camel_case(snake_case: str) -> str:
    camel_case = "".join(word.capitalize() for word in snake_case.lower().split("_"))
    camel_case = camel_case[0].lower() + camel_case[1:]
    return camel_case  # noqa: RET504


def _parse_json(json: str) -> dict[any]:
    return deserialize_json(json)["subsonic-response"]


def _get_class(name: str) -> Any:  # noqa: ANN401
    return globals()[f"{name}Field"]


class _Field:
    def __init__(self, data: str | dict[str, Any]) -> None:
        if isinstance(data, str):
            self.from_json(data)
        elif isinstance(data, dict):
            self.from_dict(data)
        else:
            error = f"Don't know what to do with '{data}' (type {type(data)})"
            raise NotImplementedError(error)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    def __str__(self) -> str:
        return str(vars(self))

    def from_json(self, json: str) -> Self:
        self.from_dict(_parse_json(json))
        return self

    def from_dict(self, raw: dict[str, Any]) -> Self:
        all_annotations: dict[str, Any] = {}
        # We need to go through the MRO to get all annotations from parent classes.
        for cls in self.__class__.__mro__:
            if not issubclass(cls, _Field) or not hasattr(cls, "__annotations__"):
                continue
            all_annotations.update(cls.__annotations__)

        for variable_name, want_type in all_annotations.items():
            # Non-required fields may not be present (i.e. Subsonic optional fields).
            # If this is the case, set its value to None.
            try:
                value = raw[_snake_to_camel_case(variable_name)]
            except KeyError:
                value = None

            # Do not do any further processing if value is None.
            if value is None:
                setattr(self, variable_name, None)
                continue

            # Try to deserialize to a Pythonic object
            base_type = want_type
            origin = get_origin(want_type)

            if origin is list:
                item_type = get_args(base_type)[0]
                if issubclass(item_type, _Field):
                    value = [item_type(item) for item in value]
            elif base_type == datetime:
                value = datetime.fromisoformat(value)
            elif base_type == timedelta:
                # OpenSubsonic responses will always return durations in seconds.
                value = timedelta(seconds=value)
            elif isinstance(value, dict):
                # Treat as JSON object
                class_name = _snake_to_camel_case(variable_name)
                class_name = f"{class_name[0].upper()}{class_name[1:]}"
                value = _get_class(class_name)(value)

            setattr(self, variable_name, value)
        return self


# Fields
# From https://opensubsonic.netlify.app/docs/responses/
#  in alphabetical order


class AlbumID3Field(_Field):
    """An album from ID3 tags."""

    id: str
    """The id of the album."""
    name: str
    """The album name."""
    version: str | None
    """OpenSubsonic additional field.
    The album version name (Remastered, Anniversary Box Set, …)."""
    artist: str | None
    """Artist name."""
    artist_id: str | None
    """The id of the artist."""
    cover_art: str | None
    """A cover_art id."""
    song_count: int
    """Number of songs."""
    duration: timedelta
    """Total duration of the album."""
    play_count: int | None
    """"""
    created: datetime
    """"""
    starred: datetime | None
    """"""
    year: int | None
    """"""
    genre: str | None
    """"""
    played: datetime | None
    """"""
    user_rating: Literal[1, 2, 3, 4, 5] | None
    """"""
    record_labels: list[RecordLabelField] | None
    """"""
    musicbrainz_id: str | None
    """"""
    genres: list[ItemGenreField] | None
    """"""
    artists: list[ArtistID3Field] | None
    """"""
    display_artist: str | None
    """"""
    release_types: list[str] | None
    """"""
    moods: list[str] | None
    """"""
    sort_name: str | None
    """"""
    original_release_date: ItemDateField | None
    """"""
    release_date: ItemDateField | None
    """"""
    is_compilation: bool | None
    """"""
    explicit_status: Literal["explicit", "clean", ""] | None
    """"""
    disc_titles: list[DiscTitleField] | None
    """"""


class ArtistID3Field(_Field):
    """An artist from ID3 tags."""

    id: str
    """The id of the artist."""
    name: str
    """The artist name."""
    cover_art: str | None
    """A cover_art id."""
    artist_image_url: str | None
    """A URL to an external image source."""
    album_count: int | None
    """Artist album count."""
    starred: datetime | None
    """Date the artist was starred."""
    musicbrainz_id: str | None
    """OpenSubsonic additional field. The artist MusicBrainzID."""
    sort_name: str | None
    """OpenSubsonic additional field. The artist sort name."""
    roles: list[str] | None
    """OpenSubsonic additional field.
    The list of all roles this artist has in the library."""


class ChildField(_Field):
    """A media."""

    id: str
    """The id of the media."""
    parent: str | None
    """The id of the parent (folder/album)."""
    is_dir: bool
    """The media is a directory."""
    title: str
    """The media name."""
    album: str | None
    """The album name."""
    artist: str | None
    """The artist name."""
    track: int | None
    """The track number."""
    year: int | None
    """The media year."""
    genre: str | None
    """The media genre."""
    cover_art: str | None
    """A cover_art id."""
    size: int | None
    """The file size of the media."""
    content_type: str | None
    """The mime_type of the media."""
    suffix: str | None
    """The file suffix of the media."""
    transcoded_content_type: str | None
    """The transcoded media_type if anything should happen."""
    transcoded_suffix: str | None
    """The file suffix of the transcoded media."""
    duration: timedelta | None
    """The duration of the media."""
    bit_rate: int | None
    """The bitrate of the media."""
    bit_depth: int | None
    """OpenSubsonic additional field. The bit depth of the media."""
    sampling_rate: int | None
    """OpenSubsonic additional field. The sampling rate of the media."""
    channel_count: int | None
    """OpenSubsonic additional field. The number of channels in the media."""
    path: str | None
    """The full path of hte media."""
    is_video: bool | None
    """Media is a video."""
    user_rating: Literal[1, 2, 3, 4, 5] | None
    """The user rating of the media."""
    average_rating: Annotated[float, ValueRange(1.0, 5.0)] | None
    """The average rating of the media."""
    play_count: int | None
    """The play count."""
    disc_number: int | None
    """The disc number."""
    created: datetime | None
    """Date the media was created."""
    starred: datetime | None
    """Date the media was starred."""
    album_id: str | None
    """The corresponding album id."""
    artist_id: str | None
    """The corresponding artist id."""
    type: Literal["music", "podcast", "audiobook", "video"] | None
    """The generic type of media."""
    media_type: Literal["song", "album", "artist"] | None
    """OpenSubsonic additional field. The actual media type [song/album/artist].
    **Note**: If you support ``musicbrainz_id`` you must support this field to ensure
    clients knows what the ID refers to."""
    bookmark_position: timedelta | None
    """The bookmark position."""
    original_width: int | None
    """The video's original width."""
    original_height: int | None
    """The video's original height."""
    played: datetime | None
    """OpenSubsonic additional field. Date the album was last played."""
    bpm: int | None
    """OpenSubsonic additional field. The BPM of the song."""
    comment: str | None
    """OpenSubsonic additional field. The comment tag of the song."""
    sort_name: str | None
    """OpenSubsonic additional field. The song sort name."""
    musicbrainz_id: str | None
    """OpenSubsonic additional field. The track's MusicBrainz Identifier."""
    isrc: list[str] | None
    """OpenSubsonic additional field. The track's ISRC(s)."""
    genres: list[ItemGenreField] | None
    """OpenSubsonic additional field. The list of all genres of the song."""
    artists: list[ArtistID3Field] | None
    """OpenSubsonic additional field. The list of all song artists of the song.
    (Note: Only the required ``ArtistID3Field`` fields should be returned by default)"""
    display_artist: str | None
    """OpenSubsonic additional field. The single value display artist."""
    album_artists: list[ArtistID3Field] | None
    """OpenSubsonic additional field. The list of all album artists of the song.
    (Note: Only the required ``ArtistID3Field`` fields should be returned by default)"""
    display_album_artist: str | None
    """OpenSubsonic additional field. The single value display album artist."""
    contributors: list[ContributorField] | None
    """OpenSubsonic additional field.
    The list of all contributor artists of the song."""
    display_composer: str | None
    """OpenSubsonic additional field. The single value display composer."""
    moods: list[str] | None
    """OpenSubsonic additional field. The list of all moods of the song."""
    replaygain: ReplayGainField | None
    """OpenSubsonic additional field. The ReplayGain data of the song."""
    explicit_status: Literal["explicit", "clean", "", 1, 2, 4] | None
    """OpenSubsonic additional field.
    (For songs extracted from tags “ITUNESADVISORY”: 1 = explicit, 2 = clean,
    MP4 “rtng”: 1 or 4 = explicit, 2 = clean. See ``AlbumID3Response`` for albums)"""


class ContributorField(_Field):
    """OpenSubsonic additional field. A contributor artist for a song or an album."""

    role: str
    """OpenSubsonic additional field. The contributor role."""
    sub_role: str
    """OpenSubsonic additional field. The subRole for roles that may require it.
    Ex: The instrument for the performer role (TMCL/performer tags).
    **Note:** For consistency between different tag formats, the TIPL sub roles should
    be directly exposed in the role field."""
    artist: ArtistID3Field
    """OpenSubsonic additional field. The artist taking on the role.
    (Note: Only the required ``ArtistID3Field`` fields should be returned by default)"""


class DirectoryField(_Field):
    """Directory."""

    id: str
    """The id."""
    parent: str | None
    """Parent item."""
    name: str
    """The directory name."""
    starred: datetime | None
    """Starred date."""
    user_rating: Literal[1, 2, 3, 4, 5] | None
    """The user rating."""
    average_rating: Annotated[float, ValueRange(1.0, 5.0)] | None
    """The average rating."""
    play_count: int | None
    """The play count."""
    child: list[ChildField] | None
    """The directory content."""


class DiscTitleField(_Field):
    """OpenSubsonic additional field. A disc title for an album."""

    disc: int
    """OpenSubsonic additional field. The disc number."""
    title: str
    """OpenSubsonic additional field. The name of the disc."""


class ErrorField(_Field):
    """Error."""

    code: Literal[0, 10, 20, 30, 40, 41, 42, 43, 44, 50, 60, 70]
    """The error code"""
    message: str | None
    """The optional error message"""
    help_url: str | None
    """OpenSubsonic additional field.
    A URL (documentation, configuration, etc) which may provide additional context for
    the error)"""


class ItemDateField(_Field):
    """OpenSubsonic additional field.
    A date for a media item that may be just a year, or year-month, or full date.
    """

    year: int | None
    """OpenSubsonic additional field. The year."""
    month: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] | None
    """OpenSubsonic additional field. The month."""
    day: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9,
                 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
                 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                 30, 31] | None  # fmt: skip
    """OpenSubsonic additional field. The day."""


class ItemGenreField(_Field):
    """OpenSubsonic additional field. A genre returned in list of genres for an item."""

    name: str
    """OpenSubsonic additional field. Genre name."""


class MusicFolderField(_Field):
    """Music folder."""

    id: int
    """The id."""
    name: str | None
    """The folder name."""


class MusicFoldersField(_Field):
    """Music folders."""

    music_folder: list[MusicFolderField]
    """The folders."""


class RecordLabelField(_Field):
    """OpenSubsonic additional field. A record label for an album."""

    name: str
    """OpenSubsonic additional field. The record label name."""


class ReplayGainField(_Field):
    """OpenSubsonic additional field. The ReplayGain data of a song."""

    track_gain: float | None
    """OpenSubsonic additional field. The track's ReplayGain value. (In dB)"""
    album_gain: float | None
    """OpenSubsonic additional field. The album's ReplayGain value. (In dB)"""
    track_peak: Annotated[float, ValueRange(0, None)] | None
    """OpenSubsonic additional field. The track peak value."""
    album_peak: Annotated[float, ValueRange(0, None)] | None
    """OpenSubsonic additional field. The album peak value."""
    base_gain: float | None
    """OpenSubsonic additional field. The base gain value. (In dB)
    (Ogg Opus Output Gain for example)"""
    fallback_gain: float | None
    """OpenSubsonic additional field.
    An optional fallback gain that clients should apply when the corresponding gain
    value is missing. (Can be computed from the tracks or exposed as an user setting.)
    """
