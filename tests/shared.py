from os import environ as env

from dotenv import load_dotenv

from pysonic import OpenSubsonic

load_dotenv()


def get_opensubsonic() -> OpenSubsonic:
    return OpenSubsonic(
        "pysonic testing ok",
        env["SUBSONIC_URL"],
        env["SUBSONIC_USER"],
        env["SUBSONIC_PASS"],
    )


def get_bad_opensubsonic() -> OpenSubsonic:
    return OpenSubsonic(
        "pysonic testing bad",
        env["SUBSONIC_URL"],
        "bad_user",
        "bad_pass",
        False  # noqa: FBT003
    )


def get_invalid_opensubsonic() -> OpenSubsonic:
    return OpenSubsonic(
        "pysonic testing invalid",
        "http://localhost:1",
        "bad_user",
        "bad_pass",
        False  # noqa: FBT003
    )

on_navidrome = get_opensubsonic().ping().type == "navidrome"
