#!/usr/bin/env python3
"""Apply the named/unnamed client-copy toggle (live-true minimal branch).

The public copy must default to the client-unnamed variants until Owen
explicitly confirms disclosure permission for Anthropic and Amazon
(see the handoff guardrails). This tool rewrites the marked CLIENT-COPY
regions in index.html so the served HTML always matches site.config.json —
the named text never sits hidden in the source.

Usage:
    python3 tools/apply_client_copy.py            # apply site.config.json
    python3 tools/apply_client_copy.py --check    # verify HTML matches config
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "site.config.json"
INDEX = ROOT / "index.html"

REGIONS = {
    "STRIP": {
        "named": '<p class="context-copy">Data and evaluation work supporting <strong>Anthropic</strong> and <strong>Amazon</strong> through external AI data partners.</p>',
        "unnamed": '<p class="context-copy">Data and evaluation work supporting <strong>frontier AI and technology organizations</strong> through external AI data partners.</p>',
    },
    "SELECTED": {
        "named": "<p>Selected projects have included managing data and evaluation work supporting Anthropic model development through an external AI data partner.</p>",
        "unnamed": "<p>Selected projects have included managing data and evaluation work supporting a frontier AI lab through an external AI data partner.</p>",
    },
    "DISCLOSURE": {
        "named": "<p><strong>Relationship context:</strong> References to named organizations describe project work supported through external AI data partners. They do not imply employment, endorsement, or a direct commercial relationship between those organizations and Learning Voyage LLC. Named references should be published only where governing agreements permit disclosure.</p>",
        "unnamed": "<p><strong>Relationship context:</strong> Project descriptions are deliberately generalized to protect confidential client and partner information. Work described here was performed through external AI data partners; nothing on this page implies employment by, endorsement by, or a direct commercial relationship with any end client.</p>",
    },
}

REGION_RE = {
    key: re.compile(
        r"(<!-- CLIENT-COPY:%s:START -->)(.*?)(<!-- CLIENT-COPY:%s:END -->)" % (key, key),
        re.S,
    )
    for key in REGIONS
}


def load_mode() -> str:
    mode = json.loads(CONFIG.read_text(encoding="utf-8")).get("clientNames")
    if mode not in ("named", "unnamed"):
        raise SystemExit(f"site.config.json: clientNames must be 'named' or 'unnamed', got {mode!r}")
    return mode


def render(html: str, mode: str) -> str:
    for key, pattern in REGION_RE.items():
        match = pattern.search(html)
        if not match:
            raise SystemExit(f"index.html: CLIENT-COPY:{key} markers not found")
        line_start = html.rfind("\n", 0, match.start(1)) + 1
        indent = html[line_start:match.start(1)]
        replacement = "%s\n%s%s\n%s%s" % (match.group(1), indent, REGIONS[key][mode], indent, match.group(3))
        html = pattern.sub(lambda _: replacement, html, count=1)
    return html


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify without writing")
    args = parser.parse_args()

    mode = load_mode()
    html = INDEX.read_text(encoding="utf-8")
    expected = render(html, mode)

    if args.check:
        if html == expected:
            print(f"OK: index.html matches site.config.json (clientNames={mode!r})")
            return 0
        print(f"DRIFT: index.html does not match clientNames={mode!r}; run tools/apply_client_copy.py")
        return 1

    if html == expected:
        print(f"Already in sync (clientNames={mode!r}); nothing to do.")
        return 0
    INDEX.write_text(expected, encoding="utf-8")
    print(f"index.html updated to clientNames={mode!r}.")
    if mode == "named":
        print("Reminder: publish named clients only after Owen confirms disclosure permission "
              "for BOTH organizations under the governing agreements.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
