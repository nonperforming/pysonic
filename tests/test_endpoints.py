from os import environ as env

import pytest
from dotenv import load_dotenv

from pysonic import OpenSubsonic

load_dotenv()

@pytest.fixture
def opensubsonic() -> OpenSubsonic:
    return OpenSubsonic(
        "pysonic testing",
        env["SUBSONIC_URL"],
        env["SUBSONIC_USER"],
        env["SUBSONIC_PASS"],
    )


class TestEndpoints:
    """Test OpenSubsonic endpoints."""

    def test_ping(self, opensubsonic: OpenSubsonic):
        assert opensubsonic.ping().is_response_ok()
