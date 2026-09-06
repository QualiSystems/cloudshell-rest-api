from __future__ import annotations

import re

from requests import Request


def file_matcher(file_name: str, file_content: bytes):
    name_pattern = re.compile(rf"filename=[\"']{file_name}[\"']".encode())
    content_pattern = re.compile(rb"\s" + file_content + rb"\s")

    def match(req: Request) -> tuple[bool, str]:
        body = req.body
        if hasattr(body, "to_string"):  # requests_toolbelt MultipartEncoder
            body = body.to_string()
        elif hasattr(body, "read"):  # file-like body
            body = body.read()

        if not name_pattern.search(body) or not content_pattern.search(body):
            res = (False, "File not found in request")
        else:
            res = (True, "")

        return res

    return match
