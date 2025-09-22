import pytest

from pysonic import OpenSubsonic

from .shared import on_navidrome

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

    def test_ping_ok(self, opensubsonic: OpenSubsonic):
        assert opensubsonic.ping().is_response_ok()

    def test_ping_bad(self, bad_opensubsonic: OpenSubsonic):
        assert not bad_opensubsonic.ping().is_response_ok()
