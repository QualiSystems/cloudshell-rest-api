from __future__ import annotations

import re

from requests import Request


def file_matcher(file_name: str, file_content: bytes):
    name_pattern = re.compile(rf"filename=[\"']{file_name}[\"']".encode())
    content_pattern = re.compile(rb"\s" + file_content + rb"\s")

    def match(req: Request) -> tuple[bool, str]:
        body = req.body.to_string()

        if not name_pattern.search(body) or not content_pattern.search(body):
            res = (False, "File not found in request")
        else:
            res = (True, "")

        return res

    return match
