class UserInfo(object):
    """User info model.

    :type user_name: str
    :type email: str
    """

    def __init__(self, info_dict):
        self.user_name = info_dict["Username"]
        self.email = info_dict["Email"]

    def __repr__(self):
        return "<UserInfo Username:{0.user_name}, Email:{0.email}>".format(self)


class ExecutionEnvironmentType(object):
    """Execution environment type model.

    :type position: int
    :type path str
    """

    def __init__(self, info_dict):
        self.position = info_dict["Position"]
        self.path = info_dict["Path"]

    def __repr__(self):
        return (
            "<ExecutionEnvironmentType Position:{0.position}, "
            "Path:{0.path}>".format(self)
        )


class ShellInfo(object):
    """Shell info model.

    :type id_: str
    :type name: str
    :type version: str
    :type standard_type: str
    :type modification_date: str
    :type last_modified_by_user: UserInfo
    :type author: str
    :type is_official: bool
    :type based_on: str
    :type execution_environment_type: ExecutionEnvironmentType
    """

    def __init__(self, info_dict):
        self.id_ = info_dict["Id"]
        self.name = info_dict["Name"]
        self.version = info_dict["Version"]
        self.standard_type = info_dict["StandardType"]
        self.modification_date = info_dict["ModificationDate"]
        self.last_modified_by_user = UserInfo(info_dict["LastModifiedByUser"])
        self.author = info_dict["Author"]
        self.is_official = info_dict["IsOfficial"]
        self.based_on = info_dict["BasedOn"]
        self.execution_environment_type = ExecutionEnvironmentType(
            info_dict["ExecutionEnvironmentType"]
        )

    def __repr__(self):
        return "<ShellInfo Name:{0.name}, Version: {0.version}>".format(self)


class StandardInfo(object):
    """Standard Info model.

    :type standard_name: str
    :type versions: list[str]
    """

    def __init__(self, info_dict):
        self.standard_name = info_dict["StandardName"]
        self.versions = info_dict["Versions"]

    def __repr__(self):
        return "<StandardInfo Name:{0.standard_name}, Versions:{0.versions}>".format(
            self
        )
