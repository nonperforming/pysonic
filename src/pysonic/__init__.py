"""A pythonic wrapper for OpenSubsonic's REST API."""

from hashlib import md5
from secrets import choice
from string import printable
from typing import TYPE_CHECKING

from httpx import Client

from . import responses

if TYPE_CHECKING:
    from httpx import Response


class OpenSubsonic:
    """Represents a connection to an OpenSubsonic server."""

    client: str
    """Client name."""
    username: str
    """Username."""

    _salt: str
    """Salt for the user's password."""
    _token: str
    """Token to authenticate with.
        This is the MD5 hash of the user's password and `_salt`,
        which are concatenated together as UTF-8 strings.
    """
    _client: Client
    """httpx client.
    """

    def __init__(self,
                 client: str,
                 url: str,
                 username: str,
                 password: str,
                 test_connection: bool = True) -> None:  # noqa: FBT001, FBT002
        """Create a new OpenSubsonic client.

        Args:
            client (str): Client name.
            url (str): Base URL. Include subdirectory and protocol,
                but do not include a trailing slash.
                Example: "https://navidrome:4533/navidrome".
            username (str): Username to authenticate with.
            password (str): Password to authenticate with.
            test_connection (bool, optional): Test if the connection is valid.
                Defaults to True.

        Raises:
            ConnectionError: If ``test_connection`` and the connection is not valid.
        """
        self.client = client
        self.username = username

        self._salt = self._get_salt()
        self._token = self._get_token(password, self._salt)
        self._client = Client(base_url=f"{url}/rest")

        if test_connection:
            ping = self.ping()
            if not ping.is_response_ok():
                error = "Failed to connect to OpenSubsonic"
                raise ConnectionError(error)

    def __del__(self) -> None:
        """Tear down the client."""
        self._client.close()

    # region Endpoints
    # Sort endpoints by alphabetical order
    def add_chat_message(self, message: str) -> responses.SubsonicResponse:
        """Adds a message to the chat log.

        Args:
            message (str): The chat message.

        Returns:
            responses.SubsonicResponse: An empty ``responses.SubsonicResponse`` element
            on success.
        """
        request = self._authenticated_request_to("addChatMessage", message=message)
        return responses.SubsonicResponse(request.text)

    def change_password(
        self, username: str, password: str
    ) -> responses.SubsonicResponse:
        """Changes the password of an existing user on the server, using the following
            parameters. You can only change your own password unless you have admin
            privileges.

        Args:
            username (str): The name of the user which should change its password.
            password (str): The new password of the new user, either in clear text of
                hex-encoded (see above).

        Returns:
            responses.SubsonicResponse: An empty ``responses.SubsonicResponse`` element
            on success.
        """
        request = self._authenticated_request_to(
            "addChatMessage", username=username, password=password
        )
        return responses.SubsonicResponse(request.text)

    def create_bookmark(
        self, id: str, position: float, comment: str | None = None  # noqa: A002
    ) -> responses.SubsonicResponse:
        """Creates or updates a bookmark (a position within a media file).
        Bookmarks are personal and not visible to other users.

        Args:
            id (str): ID of the media file to bookmark. If a bookmark already exists for
                this file it will be overwritten.
            position (float): The position (in milliseconds) within the media file.
            comment (str | None, optional): A user-defined comment.

        Returns:
            responses.SubsonicResponse: An empty ``responses.SubsonicResponse`` element
            on success.
        """
        if comment is None:
            request = self._authenticated_request_to(
                "createBookmark", id=id, position=position
            )
        else:
            request = self._authenticated_request_to(
                "createBookmark", id=id, position=position, comment=comment
            )
        return responses.SubsonicResponse(request.text)

    def download(self, id: str) -> bytes | responses.SubsonicResponse:  # noqa: A002
        """Downloads a given media file. Similar to ``stream``, but this method returns
        the original media data without transcoding or downsampling.

        Args:
            id (str): A string which uniquely identifies the file to stream. Obtained by
                calls to ``get_music_directory``.

        Returns:
            bytes | responses.SubsonicResponse: Returns binary data on success, or
                ``responses.SubsonicResponse`` on error.
        """
        request = self._authenticated_request_to("download", id=id)
        if "application/xml" in request.headers["Accept"]:
            # Request failed. Server returns HTTP 200 for some reason.
            # Yes, Accept returns application/xml instead of text/xml as advertised on https://opensubsonic.netlify.app/docs/responses/directory/
            #   or application/json as requested.
            return responses.SubsonicResponse(request.text)

        return request.content

    def ping(self) -> responses.SubsonicResponse:
        """Test connectivity with the server.

        Returns:
            responses.SubsonicResponse: An empty ``responses.SubsonicResponse`` element
            on success.
        """
        request = self._authenticated_request_to("ping")
        return responses.SubsonicResponse(request.text)

    # region Internal workings

    def _get_params(self, **kwargs: dict[str, str]) -> dict[str, str]:
        return {
            "u": self.username,
            "t": self._token,
            "s": self._salt,
            "v": "1.16.1",
            "c": self.client,
            "f": "json",
            **kwargs,
        }  # pyright: ignore[reportUnknownVariableType]

    def _authenticated_request_to(
        self, endpoint: str, **kwargs: dict[any, any]
    ) -> "Response":
        return self._client.get(f"/{endpoint}", params=self._get_params(**kwargs))

    @staticmethod
    def _is_response_ok(response: dict[any]) -> bool:
        if response["subsonic-response"]["status"] != "ok":
            error = (
                f"{response['subsonic-response']['error']['code']}: "
                f"{response['subsonic-response']['error']['message']}"
            )
            raise ConnectionError(error)
        return True

    @staticmethod
    def _get_salt() -> str:
        salt = ""
        for _ in range(16):
            salt += choice(printable)
        return salt

    @staticmethod
    def _get_token(password: str, salt: str) -> str:
        # UP012: for clarity and future-proofing
        return md5(f"{password}{salt}".encode("utf-8")).hexdigest()  # noqa: S324, UP012

    # endregion
