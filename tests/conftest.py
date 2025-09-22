import pytest

from pysonic import OpenSubsonic

from . import shared


@pytest.fixture
def opensubsonic() -> OpenSubsonic:
    return shared.get_opensubsonic()


@pytest.fixture
def bad_opensubsonic() -> OpenSubsonic:
    return shared.get_bad_opensubsonic()
