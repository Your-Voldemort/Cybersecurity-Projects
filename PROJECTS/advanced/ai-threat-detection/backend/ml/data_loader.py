"""
©AngelaMos | 2026
data_loader.py
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path

import numpy as np

from app.core.features.encoder import encode_for_inference
from app.core.features.extractor import extract_request_features
from app.core.ingestion.parsers import ParsedLogEntry

logger = logging.getLogger(__name__)

_REQUEST_LINE_RE = re.compile(
    r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH|TRACE)"
    r"\s+(\S+)\s+(HTTP/\d\.\d)\s*$"
)

_DEFAULT_IP = "192.168.1.100"

_DEFAULT_UA = (
    "Mozilla/5.0 (compatible; Konqueror/3.5; Linux)"
    " KHTML/3.5.8 (like Gecko)"
)

_WINDOWED_FEATURE_NAMES: list[str] = [
    "req_count_1m",
    "req_count_5m",
    "req_count_10m",
    "error_rate_5m",
    "unique_paths_5m",
    "unique_uas_10m",
    "method_entropy_5m",
    "avg_response_size_5m",
    "status_diversity_5m",
    "path_depth_variance_5m",
    "inter_request_time_mean",
    "inter_request_time_std",
]


@dataclass
class CSICRequest:
    """
    Single HTTP request parsed from CSIC 2010 dataset format
    """

    method: str
    path: str
    query_string: str
    protocol: str
    headers: dict[str, str]
    body: str
    label: int


def parse_csic_file(
    path: Path,
    label: int,
) -> list[CSICRequest]:
    """
    Parse a CSIC 2010 dataset file into a list of CSICRequest objects
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    blocks: list[list[str]] = []
    current: list[str] = []

    for line in lines:
        match = _REQUEST_LINE_RE.match(line)
        if match and current:
            blocks.append(current)
            current = [line]
        elif match:
            current = [line]
        elif current:
            current.append(line)

    if current:
        blocks.append(current)

    results: list[CSICRequest] = []
    for block in blocks:
        req = _parse_request_block(block, label)
        if req is not None:
            results.append(req)

    logger.info(
        "Parsed %d requests from %s (label=%d)",
        len(results),
        path.name,
        label,
    )
    return results


def _parse_request_block(
    lines: list[str],
    label: int,
) -> CSICRequest | None:
    """
    Parse a single request block into a CSICRequest
    """
    if not lines:
        return None

    match = _REQUEST_LINE_RE.match(lines[0])
    if not match:
        return None

    method = match.group(1)
    full_uri = match.group(2)
    protocol = match.group(3)

    if "?" in full_uri:
        path, query_string = full_uri.split("?", 1)
    else:
        path = full_uri
        query_string = ""

    headers: dict[str, str] = {}
    body_start = len(lines)

    for i, line in enumerate(lines[1:], 1):
        if not line.strip():
            body_start = i + 1
            break
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key] = value

    body_lines = [
        ln for ln in lines[body_start:] if ln.strip()
    ]
    body = "\n".join(body_lines)

    return CSICRequest(
        method=method,
        path=path,
        query_string=query_string,
        protocol=protocol,
        headers=headers,
        body=body,
        label=label,
    )


def csic_to_parsed_entry(req: CSICRequest) -> ParsedLogEntry:
    """
    Convert a CSICRequest to a ParsedLogEntry with synthesized defaults
    for fields not present in the CSIC dataset
    """
    ua = req.headers.get("User-Agent", _DEFAULT_UA)

    query = req.query_string
    if req.body:
        query = (
            f"{query}&{req.body}" if query else req.body
        )

    return ParsedLogEntry(
        ip=_DEFAULT_IP,
        timestamp=datetime.now(UTC),
        method=req.method,
        path=req.path,
        query_string=query,
        status_code=200,
        response_size=0,
        referer="",
        user_agent=ua,
        raw_line="",
    )


def load_csic_dataset(
    normal_path: Path,
    attack_path: Path,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Load CSIC 2010 normal and attack files, extract features,
    and return (X, y) arrays ready for model training
    """
    normal_reqs = parse_csic_file(normal_path, label=0)
    attack_reqs = parse_csic_file(attack_path, label=1)

    all_reqs = normal_reqs + attack_reqs

    vectors: list[list[float]] = []
    labels: list[int] = []

    for req in all_reqs:
        entry = csic_to_parsed_entry(req)
        features = extract_request_features(entry)

        for name in _WINDOWED_FEATURE_NAMES:
            features[name] = 0.0

        vector = encode_for_inference(features)
        vectors.append(vector)
        labels.append(req.label)

    X = np.array(vectors, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    logger.info(
        "Dataset loaded: X=%s, y=%s (normal=%d, attack=%d)",
        X.shape,
        y.shape,
        np.sum(y == 0),
        np.sum(y == 1),
    )

    return X, y
