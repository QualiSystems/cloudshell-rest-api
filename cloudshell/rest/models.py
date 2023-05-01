from __future__ import annotations

from attrs import define, field
from typing_extensions import Self


@define
class UserInfo:
    user_name: str
    email: str

    @classmethod
    def from_dict(cls, info_dict: dict) -> Self:
        return cls(
            user_name=info_dict["Username"],
            email=info_dict["Email"],
        )


@define
class ExecutionEnvironmentType:
    position: int
    path: str

    @classmethod
    def from_dict(cls, info_dict: dict) -> Self:
        return cls(
            position=info_dict["Position"],
            path=info_dict["Path"],
        )


@define
class ShellInfo:
    id: str = field(repr=False)  # noqa: A003
    name: str
    version: str
    standard_type: str = field(repr=False)
    modification_date: str = field(repr=False)
    last_modified_by_user: UserInfo = field(repr=False)
    author: str = field(repr=False)
    is_official: bool
    based_on: str = field(repr=False)
    execution_environment_type: ExecutionEnvironmentType = field(repr=False)

    @classmethod
    def from_dict(cls, info_dict: dict) -> Self:
        return cls(
            id=info_dict["Id"],
            name=info_dict["Name"],
            version=info_dict["Version"],
            standard_type=info_dict["StandardType"],
            modification_date=info_dict["ModificationDate"],
            last_modified_by_user=UserInfo.from_dict(info_dict["LastModifiedByUser"]),
            author=info_dict["Author"],
            is_official=info_dict["IsOfficial"],
            based_on=info_dict["BasedOn"],
            execution_environment_type=ExecutionEnvironmentType.from_dict(
                info_dict["ExecutionEnvironmentType"]
            ),
        )


@define
class StandardInfo:
    standard_name: str
    versions: list[str]

    @classmethod
    def from_dict(cls, info_dict: dict) -> Self:
        return cls(
            standard_name=info_dict["StandardName"],
            versions=info_dict["Versions"],
        )
