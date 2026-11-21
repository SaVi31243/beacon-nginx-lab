from dataclasses import dataclass
from math import isfinite
from os import environ
from urllib.parse import SplitResult, urlsplit


@dataclass(frozen=True)
class CheckSettings:
    origin: SplitResult
    release: str
    timeout: float

    @classmethod
    def from_env(cls):
        origin = urlsplit(environ.get("BASE_URL", "").strip().rstrip("/"))
        if (
            origin.scheme not in {"http", "https"}
            or not origin.hostname
            or origin.username is not None
            or origin.path
            or origin.query
            or origin.fragment
        ):
            raise ValueError("BASE_URL must be an HTTP(S) origin")
        release = environ.get("EXPECTED_RELEASE", "").strip()
        if not release:
            raise ValueError("EXPECTED_RELEASE must contain a release identifier")
        timeout = float(environ.get("CHECK_TIMEOUT", "3"))
        if not isfinite(timeout) or timeout <= 0:
            raise ValueError("CHECK_TIMEOUT must be positive")
        return cls(origin, release, timeout)
