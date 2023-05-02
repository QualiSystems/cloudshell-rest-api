from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from alive_progress import alive_bar
from requests import Response
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor


def iter_resp_with_pb(
    resp: Response, show: bool = True, chunk: int = 4096
) -> Generator[bytes, None, None]:
    total = int(resp.headers.get("content-length", 0))

    pb_context = alive_bar(
        total,
        unit="B",
        scale=True,
        disable=not show,
    )

    with pb_context as bar:
        for data in resp.iter_content(chunk_size=chunk):
            size = len(data)
            bar(size)
            yield data


@contextmanager
def upload_with_pb(data: dict, headers: dict, show: bool = True):
    e = MultipartEncoder(data)
    pb_context = alive_bar(
        e.len,
        unit="B",
        scale=True,
        disable=not show,
    )

    with pb_context as bar:
        m = MultipartEncoderMonitor(e, _create_upload_callback(bar))
        headers["Content-Type"] = m.content_type

        yield m


def _create_upload_callback(bar):
    bytes_read = 0

    def callback(monitor):
        nonlocal bytes_read
        new_bytes = monitor.bytes_read - bytes_read
        bytes_read = monitor.bytes_read
        if new_bytes:
            bar(new_bytes)

    return callback
