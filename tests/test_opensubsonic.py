import httpx
import pytest

from pysonic import OpenSubsonic


class TestOpenSubsonic:
    """Test the OpenSubsonic class."""

    def test_okay(self, opensubsonic: OpenSubsonic):
        assert opensubsonic.ping().is_response_ok()

    def test_invalid(self):
        with pytest.raises(httpx.ConnectError):
            OpenSubsonic(
                "pysonic testing invalid",
                "http://localhost:1",
                "bad_user",
                "bad_pass",
            )
