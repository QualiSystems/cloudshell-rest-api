import sys

if sys.version_info.major < 3:
    collect_ignore = ["tests/test_async_api.py"]
