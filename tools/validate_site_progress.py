#!/usr/bin/env python3
"""Fail CI on mismatched roadmap, published progress and accepted editorial checkpoint.

No third-party dependencies and no network access. The widget remains read-only:
this validator checks its publication contract, not subjective editorial truth.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {"accepted", "partial", "planned"}
errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_json(name: str) -> dict:
    try:
        content = json.loads((ROOT / name).read_text(encoding="utf-8"))
        if not isinstance(content, dict):
            raise ValueError("top-level value must be an object")
        return content
    except (OSError, ValueError) as exc:
        fail(f"{name}: {exc}")
        return {}


def integer(value: object) -> bool:
    return type(value) is int  # Do not accept JSON booleans as numbers.


def normalized_range(value: object) -> str:
    return re.sub(r"\s*[–—-]\s*", "-", str(value).strip())


def main() -> int:
    config = load_json("site-progress.json")
    state = load_json("CURRENT-STATE.json")
    try:
        document = (ROOT / "ROADMAP-COVERAGE.md").read_text(encoding="utf-8")
        widget = (ROOT / "site-progress.js").read_text(encoding="utf-8")
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"Missing required roadmap publication file: {exc}")
        document = widget = index = agents = ""

    if config.get("schemaVersion") != 1 or config.get("project") != "Compulsive-Research":
        fail("site-progress.json must declare schemaVersion 1 and Compulsive-Research")

    try:
        reviewed = dt.date.fromisoformat(config["asOf"])
        if reviewed > dt.date.today() + dt.timedelta(days=1):
            fail("site-progress.json asOf is in the future")
    except (TypeError, ValueError, KeyError):
        fail("site-progress.json asOf must be an ISO calendar date")

    roadmap = config.get("roadmap")
    roadmap = roadmap if isinstance(roadmap, dict) else {}
    if roadmap.get("document") != "ROADMAP-COVERAGE.md":
        fail("Progress manifest must link to governing ROADMAP-COVERAGE.md")
    gates = roadmap.get("gates")
    if not isinstance(gates, list) or not gates:
        fail("Progress manifest must have nonempty roadmap gates")
        gates = []

    ids: set[str] = set()
    total = accepted = 0
    for n, gate in enumerate(gates, 1):
        if not isinstance(gate, dict):
            fail(f"Gate {n}: expected object")
            continue
        gate_id = gate.get("id")
        weight = gate.get("weight")
        label = gate.get("label")
        status = gate.get("status")
        evidence = gate.get("evidence")
        if not isinstance(gate_id, str) or not re.fullmatch(r"[a-z0-9-]{2,64}", gate_id):
            fail(f"Gate {n}: invalid stable ID")
        elif gate_id in ids:
            fail(f"Gate {n}: repeated ID {gate_id}")
        ids.add(str(gate_id))
        if not isinstance(label, str) or not label.strip():
            fail(f"Gate {n}: missing human-readable label")
        if not isinstance(evidence, str) or not evidence.strip():
            fail(f"Gate {n}: missing evidence pointer")
        if not integer(weight) or weight < 1:
            fail(f"Gate {n}: weight must be a positive integer")
            weight = 0
        if status not in VALID_STATUSES:
            fail(f"Gate {n}: status must be accepted, planned or partial")
        total += weight
        if status == "accepted":
            accepted += weight

    if total != 100:
        fail(f"Roadmap weights must total 100; found {total}")

    # Match every published gate to the authoritative markdown acceptance table.
    # Avoid parsing arbitrary prose by locating the table's unique heading.
    table = document.split("| Current finite approved delivery gate |", 1)
    if len(table) != 2:
        fail("Governing roadmap missing canonical gate table")
        documented = []
    else:
        section = table[1].split("\n\n", 1)[0]
        documented = re.findall(
            r"^\|\s*(.*?)\s*\|\s*(\d+)\s*\|\s*(accepted|partial|planned)\s*\|",
            section, re.MULTILINE
        )
    if len(documented) != len(gates):
        fail(f"Gate table has {len(documented)} rows; manifest has {len(gates)}")
    for n, (row, gate) in enumerate(zip(documented, gates), 1):
        label, weight_text, status = row
        if (label.strip(), int(weight_text), status) != (
            gate.get("label"), gate.get("weight"), gate.get("status")
        ):
            fail(f"Gate {n}: roadmap table differs from site-progress.json")

    summary = re.search(
        r"\*\*Overall accepted:\s*(\d+)/100\s*=\s*(\d+)%\*\*",
        document
    )
    if not summary:
        fail("Roadmap missing auditable overall acceptance statement")
    elif int(summary[1]) != accepted or int(summary[2]) != accepted:
        fail(f"Roadmap narrative says {summary[1]}/{summary[2]} but accepted weight is {accepted}")

    phase = config.get("progress")
    phase = phase if isinstance(phase, dict) else {}
    checkpoint = state.get("readerV31LatestCheckpoint")
    checkpoint = checkpoint if isinstance(checkpoint, dict) else {}
    next_article = checkpoint.get("nextArticle")
    if not integer(next_article) or not 1 <= next_article <= 1001:
        fail("CURRENT-STATE.json latest Reader checkpoint has invalid nextArticle")
    else:
        completed = next_article - 1
        if phase.get("completed") != completed or phase.get("total") != 100:
            fail(f"Reader phase must publish {completed}/100 from CURRENT-STATE.json; got {phase.get('completed')}/{phase.get('total')}")
    entries = checkpoint.get("entries", "")
    fallback = normalized_range(config.get("revision", ""))
    if entries and normalized_range(entries) not in fallback:
        fail(f"Fallback revision must reflect latest accepted Reader wave {entries}")

    source = config.get("revisionSource")
    if not isinstance(source, dict) or (
        source.get("type"), source.get("file"), source.get("path")
    ) != ("json", "CURRENT-STATE.json", "readerV31LatestCheckpoint.entries"):
        fail("Revision must resolve from CURRENT-STATE.json readerV31LatestCheckpoint.entries")
    if not state.get("readerV31LatestCheckpoint"):
        fail("No accepted Reader checkpoint found in CURRENT-STATE.json")

    if index.count('src="./site-progress.js"') != 1:
        fail("Landing page must mount exactly one read-only progress script")
    if "getText('site-progress.json')" not in widget or "roadmapFor(config)" not in widget:
        fail("Status script no longer reads the structured roadmap")
    if "ROADMAP-COVERAGE.md" not in agents or "site-progress.json" not in agents:
        fail("AGENTS.md must route workers to the roadmap and status manifest")

    if errors:
        for problem in errors:
            print("ERROR:", problem, file=sys.stderr)
        print(f"FAIL: {len(errors)} roadmap/status integrity issue(s)", file=sys.stderr)
        return 1
    print(
        f"PASS: {len(gates)} synchronized roadmap gates; "
        f"{accepted}/100 weighted accepted; "
        f"Reader {phase['completed']}/100; checkpoint {entries}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
