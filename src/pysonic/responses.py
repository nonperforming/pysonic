"""OpenSubsonic responses."""

from __future__ import annotations

from json import loads as deserialize_json
from re import compile as regex_compile
from typing import Any, Literal, Self

camel_case_to_snake_case_pattern = regex_compile(r"(?<!^)(?=[A-Z])")


def _camel_to_snake_case(camel_case: str) -> str:
    return camel_case_to_snake_case_pattern.sub("_", camel_case).lower()


def _snake_to_camel_case(snake_case: str) -> str:
    camel_case = "".join(word.capitalize() for word in snake_case.lower().split("_"))
    camel_case = camel_case[0].lower() + camel_case[1:]
    return camel_case


def _parse_json(json: str) -> dict[any]:
    return deserialize_json(json)["subsonic-response"]


def _get_class(name: str) -> Any:  # noqa: ANN401
    return globals()[name]


# From https://opensubsonic.netlify.app/docs/responses/
#  in alphabetical order


class _BaseResponse:
    def __init__(self, data: str | dict) -> Self:
        if isinstance(data, str):
            self.from_json(data)
        elif isinstance(data, dict):
            self.from_dict(data)
        else:
            error = f"Don't know what to do with '{data}' (type {type(data)})"
            raise NotImplementedError(error)

    def from_json(self, json: str) -> Self:
        self.from_dict(_parse_json(json))

    def from_dict(self, raw: dict) -> Self:
        for variable_name in vars(self.__class__)["__annotations__"]:
            try:
                value = raw[_snake_to_camel_case(variable_name)]
            except KeyError:
                # Non-required fields may not be present.
                value = None

            if isinstance(value, dict):
                # Treat as JSON object
                value = _get_class(_camel_to_snake_case(variable_name).title())(value)

            setattr(self, variable_name, value)


class SubsonicResponse(_BaseResponse):
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
    error: Error | None
    """The error details when status is ``failed``"""

    def is_response_ok(self) -> bool:
        """Returns ``True`` if the response is ok.

        Returns:
            bool: ``True`` if the response is ok.
        """
        return self.status == "ok"


class Error(_BaseResponse):
    """Error."""

    code: Literal[0, 10, 20, 30, 40, 41, 42, 43, 44, 50, 60, 70]
    """The error code"""
    message: str | None
    """The optional error message"""
    help_url: str | None
    """OpenSubsonic additional field.
    A URL (documentation, configuration, etc) which may provide additional context for
     the error)"""
