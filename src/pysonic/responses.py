"""OpenSubsonic responses."""

from __future__ import annotations

from typing import Literal

from . import fields


# Must be first otherwise we cannot subclass it
class SubsonicResponse(fields._Field):  # noqa: SLF001
    """Common answer wrapper."""

    status: Literal["ok", "failure"]
    """The command result. ``ok`` or ``failed``"""
    version: str
    """The server supported Subsonic API version."""
    type: str | None
    """OpenSubsonic additional field.
    The server actual name. [Ex: ``Navidrome`` or ``gonic``]"""
    server_version: str | None
    """OpenSubsonic additional field.
    The server actual version. [Ex: ``1.2.3 (beta)``]"""
    open_subsonic: bool | None
    """OpenSubsonic additional field.
    Must return true if the server support OpenSubsonic API v1"""
    error: fields.ErrorField | None
    """The error details when status is ``failed``"""

    def is_response_ok(self) -> bool:
        """Returns ``True`` if the response is ok.

        Returns:
            bool: ``True`` if the response is ok.
        """
        return self.status == "ok"


# From https://opensubsonic.netlify.app/docs/responses/
#  in alphabetical order
class DirectoryResponse(SubsonicResponse):
    """Directory."""

    directory: fields.DirectoryField
    """Directory."""

class MusicFoldersResponse(SubsonicResponse):
    """Music folders."""

    music_folders: list[fields.MusicFolderField]
    """Music folders."""
