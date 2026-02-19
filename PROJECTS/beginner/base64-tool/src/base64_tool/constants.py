"""
©AngelaMos | 2026
constants.py
"""

from enum import StrEnum
from typing import Final


class EncodingFormat(StrEnum):
    BASE64 = "base64"
    BASE64URL = "base64url"
    BASE32 = "base32"
    HEX = "hex"
    URL = "url"


class ExitCode:
    SUCCESS: Final[int] = 0
    ERROR: Final[int] = 1
    INVALID_INPUT: Final[int] = 2


PEEL_MAX_DEPTH: Final[int] = 20

MIN_INPUT_LENGTH: Final[int] = 4

PREVIEW_LENGTH: Final[int] = 72

CONFIDENCE_THRESHOLD: Final[float] = 0.6

PRINTABLE_RATIO_THRESHOLD: Final[float] = 0.8


class ScoreWeight:
    DECODE_SUCCESS: Final[float] = 0.15
    PRINTABLE_RESULT: Final[float] = 0.15
    LONGER_INPUT: Final[float] = 0.05

    B64_BASE: Final[float] = 0.4
    B64_VALID_PADDING: Final[float] = 0.1
    B64_SPECIAL_CHARS: Final[float] = 0.1
    B64_MIXED_CASE: Final[float] = 0.1
    B64_NO_SIGNAL_PENALTY: Final[float] = 0.2

    B64URL_BASE: Final[float] = 0.3
    B64URL_SAFE_CHARS: Final[float] = 0.25

    B32_BASE: Final[float] = 0.35
    B32_VALID_PADDING: Final[float] = 0.1
    B32_UPPERCASE: Final[float] = 0.1

    HEX_BASE: Final[float] = 0.3
    HEX_SEPARATOR_PRESENT: Final[float] = 0.2
    HEX_ALPHA_CHARS: Final[float] = 0.1
    HEX_NO_ALPHA_PENALTY: Final[float] = 0.15
    HEX_CONSISTENT_CASE: Final[float] = 0.1
    HEX_DECODE_SUCCESS: Final[float] = 0.1

    URL_BASE: Final[float] = 0.3
    URL_RATIO_MULTIPLIER: Final[float] = 0.4
    URL_RATIO_CAP: Final[float] = 0.35
    URL_DECODE_CHANGED: Final[float] = 0.15


BASE64_CHARSET: Final[
    frozenset[str]
] = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")

BASE64URL_CHARSET: Final[
    frozenset[str]
] = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=")

BASE32_CHARSET: Final[frozenset[str]] = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=")

HEX_CHARSET: Final[frozenset[str]] = frozenset("0123456789abcdefABCDEF")

HEX_SEPARATORS: Final[frozenset[str]] = frozenset(" :.-")
