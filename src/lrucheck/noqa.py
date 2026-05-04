from __future__ import annotations

import io
import re
import tokenize
from typing import Optional

NOQA_PATTERN = re.compile(r"#\s*noqa(?::\s*([A-Za-z0-9_, ]+))?", re.IGNORECASE)

NoqaMap = dict[int, Optional[frozenset[str]]]


def parse_noqa(source: str) -> NoqaMap:
    result: NoqaMap = {}
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    except tokenize.TokenError:
        return result
    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        match = NOQA_PATTERN.search(token.string)
        if match is None:
            continue
        codes_text = match.group(1)
        if codes_text is None:
            result[token.start[0]] = None
        else:
            result[token.start[0]] = frozenset(
                code.strip().upper() for code in codes_text.split(",") if code.strip()
            )
    return result


def is_suppressed(line: int, code: str, noqa_map: NoqaMap) -> bool:
    if line not in noqa_map:
        return False
    codes = noqa_map[line]
    return codes is None or code in codes
