from __future__ import annotations


class UserInfo:
    def __init__(self, info_dict: dict):
        self.user_name: str = info_dict["Username"]
        self.email: str = info_dict["Email"]

    def __repr__(self):
        return "<UserInfo Username:{0.user_name}, Email:{0.email}>".format(self)


class ExecutionEnvironmentType:
    def __init__(self, info_dict):
        self.position: int = info_dict["Position"]
        self.path: str = info_dict["Path"]

    def __repr__(self):
        return (
            "<ExecutionEnvironmentType Position:{0.position}, "
            "Path:{0.path}>".format(self)
        )


class ShellInfo:
    def __init__(self, info_dict):
        self.id: str = info_dict["Id"]
        self.name: str = info_dict["Name"]
        self.version: str = info_dict["Version"]
        self.standard_type: str = info_dict["StandardType"]
        self.modification_date: str = info_dict["ModificationDate"]
        self.last_modified_by_user = UserInfo(info_dict["LastModifiedByUser"])
        self.author: str = info_dict["Author"]
        self.is_official: bool = info_dict["IsOfficial"]
        self.based_on: str = info_dict["BasedOn"]
        self.execution_environment_type = ExecutionEnvironmentType(
            info_dict["ExecutionEnvironmentType"]
        )

    def __repr__(self):
        return "<ShellInfo Name:{0.name}, Version: {0.version}>".format(self)


class StandardInfo:
    def __init__(self, info_dict):
        self.standard_name: str = info_dict["StandardName"]
        self.versions: list[str] = info_dict["Versions"]

    def __repr__(self):
        return "<StandardInfo Name:{0.standard_name}, Versions:{0.versions}>".format(
            self
        )
