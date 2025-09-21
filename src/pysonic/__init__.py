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

    def __init__(self, client: str, url: str, username: str, password: str) -> None:
        """Create a new OpenSubsonic client.

        Args:
            client (str): Client name.
            url (str): Base URL. Include subdirectory and protocol,
                but do not include a trailing slash.
                Example: "https://navidrome:4533/navidrome".
            username (str): Username to authenticate with.
            password (str): Password to authenticate with.
        """
        self.client = client
        self.username = username

        self._salt = self._get_salt()
        self._token = self._get_token(password, self._salt)
        self._client = Client(base_url=f"{url}/rest")

    def __del__(self) -> None:
        """Tear down the client."""
        self._client.close()

    # region Endpoints
    # Sort endpoints by alphabetical order
    def ping(self) -> responses.SubsonicResponse:
        """Test connectivity with the server.

        Returns:
            responses.SubsonicResponse: The server's response.
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

    def _authenticated_request_to(self, endpoint: str) -> "Response":
        return self._client.get(f"/{endpoint}", params=self._get_params())

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
