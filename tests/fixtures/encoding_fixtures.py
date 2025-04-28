"""
UTF-8 and Locale Management Fixtures

This module provides fixtures for ensuring consistent UTF-8 encoding and
locale handling during testing, especially in subprocesses.
"""
import os
import pytest
import locale
import contextlib
from typing import Iterator


_UTF8_ENV = {
    "PYTHONIOENCODING": "utf-8",
    "LC_ALL": "C.UTF-8",
    "LANG": "C.UTF-8",
}


@contextlib.contextmanager
def _utf8_subprocess_env() -> Iterator[dict]:
    """
    Context-manager that injects UTF-8 friendly env-vars before a subprocess
    starts and rolls them back afterwards.
    """
    original = {k: os.environ.get(k) for k in ("PYTHONIOENCODING", "LC_ALL", "LANG")}
    try:
        os.environ["PYTHONIOENCODING"] = "utf-8"
        # On *nix these two control libc / locale:
        os.environ["LC_ALL"] = "C.UTF-8"
        os.environ["LANG"] = "C.UTF-8"
        yield os.environ
    finally:
        for k, v in original.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


# ----------  session-wide fixture applied to every test automatically  ---------
@pytest.fixture(scope="session", autouse=True)
def force_utf8_subprocesses() -> Iterator[None]:
    """
    Session-scoped, autouse – runs once before ANY test executes.

    * sets environment so that every child-process sees UTF-8 encodings
    * patches ``locale.getpreferredencoding`` so libraries that rely on it
      (e.g. `subprocess._readerthread` inside pytest's capture layer) won't
      fall back to CP1252 on Windows.
    """
    # 1) Patch locale
    _orig_getpref = locale.getpreferredencoding
    locale.getpreferredencoding = lambda do_setlocale=True: "UTF-8"

    # 2) Make sure *our* subprocess invocations inherit the UTF-8 env
    with _utf8_subprocess_env():
        yield

    # ---- rollback ----
    locale.getpreferredencoding = _orig_getpref  # restore environment after the entire test session