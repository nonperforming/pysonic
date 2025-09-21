from os import environ as env

import pytest
from dotenv import load_dotenv

from pysonic import OpenSubsonic

load_dotenv()


def get_opensubsonic() -> OpenSubsonic:
    return OpenSubsonic(
        "pysonic testing",
        env["SUBSONIC_URL"],
        env["SUBSONIC_USER"],
        env["SUBSONIC_PASS"],
    )


on_navidrome = get_opensubsonic().ping().type == "navidrome"


@pytest.fixture
def opensubsonic() -> OpenSubsonic:
    return get_opensubsonic()

# TODO: Create mock server to test implementation of...
#   - add_chat_message (properly),  # noqa: ERA001
#   - change_password,
#   - create_bookmark,
#   - etc.

class TestEndpoints:
    """Test OpenSubsonic endpoints."""

    @pytest.mark.skipif(on_navidrome, reason="Not implemented on Navidrome")
    def test_add_chat_message(self, opensubsonic: OpenSubsonic):
        assert opensubsonic.add_chat_message("pysonic test message").is_response_ok()

    def test_ping(self, opensubsonic: OpenSubsonic):
        assert opensubsonic.ping().is_response_ok()
