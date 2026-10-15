#!/usr/bin/env python3
"""Run the Compulsive Research continuation validation suite.

Use --quick after a localized Honorable Mention insertion and --full before release.
The wrapper preserves each command's output under audit/handoff-validation/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import tempfile
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit" / "handoff-validation"

QUICK = [
    [sys.executable, "tools/check_canonical_lock.py"],
    [sys.executable, "tools/build_manifest.py"],
    [sys.executable, "tools/validate_local_assets.py"],
    [sys.executable, "tools/validate_no_reader_facing_editorial_labels.py"],
    [sys.executable, "tools/validate_reader_layout_contract.py"],
    [sys.executable, "tools/test_reader_experience_v3_regressions.py"],
    [sys.executable, "tools/validate_reader_experience_v3.py"],
    [sys.executable, "tools/remove_editorial_study_decks.py", "--check"],
    [sys.executable, "tools/validate_honorable_template.py"],
    [sys.executable, "tools/validate_honorable_categories.py"],
]

# The full release command verifies that all V2 reports were produced against the
# exact current corpus. Use --refresh-v2 after changing article content to rebuild
# and restamp those reports.
FULL = QUICK + [
    [sys.executable, "tools/verify_release_v2_state.py"],
]

REFRESH_V2 = [
    [sys.executable, "tools/validate_editorial_quality.py", "--output-dir", "audit/editorial-v2"],
    [sys.executable, "tools/validate_canonical_identity.py", "--output-dir", "audit/canonical-identity-v2"],
    [sys.executable, "tools/validate_deck_semantics.py", "--output-dir", "audit/deck-semantics"],
    [sys.executable, "tools/validate_archive_core_v2.py", "--output-dir", "audit/archive-core-v2"],
    [sys.executable, "tools/validate_historical_decks_only.py"],
    [sys.executable, "tools/validate_deck_archives.py", "--jobs", "4", "--output-dir", "audit/deck-archives"],
    [sys.executable, "tools/validate_official_mtg_decks.py", "--jobs", "4", "--output-dir", "audit/official-mtg-decks"],
    [sys.executable, "tools/validate_card_image_links.py", "--jobs", "4", "--output-dir", "audit/card-image-links"],
    [sys.executable, "tools/stamp_release_v2_state.py"],
]

LEGACY_EXHAUSTIVE = REFRESH_V2 + [
    [sys.executable, "tools/canonicalize_wave_identity.py", "--check"],
    [sys.executable, "tools/validate_hero_migration.py", "--output-dir", "audit/hero-migration"],
    [sys.executable, "tools/validate_headline_identity.py", "--output-dir", "audit/headline-convention"],
    [sys.executable, "tools/canonicalize_artwork_spotlight.py", "--check"],
    [sys.executable, "tools/refine_artwork_captions.py", "--check"],
    [sys.executable, "tools/canonicalize_design_echo.py", "--check"],
    [sys.executable, "tools/complete_design_echo_sections.py", "--check"],
    [sys.executable, "tools/validate_design_echo.py"],
    ["node", "tools/test_printing_gallery_identity.js"],
    [sys.executable, "tools/canonicalize_printing_galleries.py", "--check"],
    [sys.executable, "tools/canonicalize_sources_heading.py", "--check"],
    [sys.executable, "tools/repair_known_historical_deck_anomalies.py", "--check"],
    [sys.executable, "tools/canonicalize_copy_decklists.py", "--check"],
    [sys.executable, "tools/render_official_mtg_deck_sections.py", "--check"],
    [sys.executable, "tools/canonicalize_card_image_links.py", "--check"],
    [sys.executable, "tools/refresh_card_name_catalog.py", "--check"],
    [sys.executable, "tools/test_card_reference_discovery.py"],
    [sys.executable, "tools/canonicalize_card_links.py", "--check"],
    [sys.executable, "tools/validate_card_links.py"],
    [sys.executable, "tools/validate_archive.py", "--jobs", "4", "--output-dir", "audit/current"],
    [sys.executable, "tools/check_audit_regression.py", "audit/baseline-2026-07-29.json", "audit/current/audit-report.json"],
]

def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quick", action="store_true", help="Run the focused continuation checks")
    mode.add_argument("--full", action="store_true", help="Run the bounded Editorial V2 release suite")
    mode.add_argument("--refresh-v2", action="store_true", help="Regenerate all Editorial V2 reports and bind them to the current corpus")
    mode.add_argument("--legacy-exhaustive", action="store_true", help="Also run retained slow migration and regression audits")
    parser.add_argument("--continue-on-failure", action="store_true", help="Run remaining commands after a failure")
    parser.add_argument("--command-timeout", type=int, default=1800, help="Maximum seconds allowed for each validator (default: 1800)")
    parser.add_argument("--stream-output", action="store_true", help="Stream child output directly instead of capturing it in per-command logs")
    parser.add_argument("--stage-start", type=int, default=1, help="First one-based validation stage to run")
    parser.add_argument("--stage-end", type=int, help="Last one-based validation stage to run (inclusive)")
    args = parser.parse_args()

    if args.legacy_exhaustive:
        commands = LEGACY_EXHAUSTIVE
        mode_name = "legacy-exhaustive"
    elif args.refresh_v2:
        commands = REFRESH_V2
        mode_name = "refresh-v2"
    elif args.full:
        commands = FULL
        mode_name = "full"
    else:
        commands = QUICK
        mode_name = "quick"
    last_stage = args.stage_end or len(commands)
    if not 1 <= args.stage_start <= last_stage <= len(commands):
        parser.error(f"stage range must be within 1..{len(commands)} and start <= end")
    partial = args.stage_start != 1 or last_stage != len(commands)
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    suffix = f"-stages-{args.stage_start:02d}-{last_stage:02d}" if partial else ""
    run_dir = OUT / f"{stamp}-{mode_name}{suffix}"
    run_dir.mkdir(parents=True)

    results: list[dict[str, object]] = []
    for index, command in enumerate(commands, start=1):
        if index < args.stage_start or index > last_stage:
            continue
        executable = command[0]
        if executable == "node" and shutil.which("node") is None:
            result = {
                "index": index,
                "command": command,
                "status": "SKIPPED",
                "returncode": None,
                "reason": "Node.js is not installed",
            }
            results.append(result)
            print(f"SKIP {index:02d}: {' '.join(command)} (Node.js unavailable)")
            continue

        print(f"RUN  {index:02d}: {' '.join(command)}", flush=True)
        log_path = run_dir / f"{index:02d}.log"
        try:
            # Run each validator with its output directed to a local temporary
            # file. Polling prints a small heartbeat so long validators remain
            # observable, while avoiding project-mount stdout stalls.
            started_at = time.monotonic()
            last_heartbeat = started_at
            if args.stream_output:
                proc = subprocess.Popen(command, cwd=ROOT, text=True)
                temp_output = None
            else:
                temp_output = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
                proc = subprocess.Popen(
                    command,
                    cwd=ROOT,
                    text=True,
                    stdout=temp_output,
                    stderr=subprocess.STDOUT,
                )
            while proc.poll() is None:
                now = time.monotonic()
                if now - started_at > args.command_timeout:
                    proc.kill()
                    proc.wait()
                    if temp_output is not None:
                        temp_output.close()
                    raise subprocess.TimeoutExpired(command, args.command_timeout)
                if now - last_heartbeat >= 5:
                    print(f"WAIT {index:02d}: validator still running ({int(now - started_at)}s)", flush=True)
                    last_heartbeat = now
                time.sleep(0.25)
            returncode = proc.returncode
            if temp_output is None:
                captured_output = "Output streamed to the invoking terminal.\n"
            else:
                temp_output.seek(0)
                captured_output = temp_output.read()
                temp_output.close()
            with log_path.open("w", encoding="utf-8") as log_handle:
                log_handle.write(f"$ {' '.join(command)}\n\nOUTPUT\n")
                log_handle.write(captured_output)
            status = "PASS" if returncode == 0 else "FAIL"
            reason = None
        except subprocess.TimeoutExpired:
            with log_path.open("a", encoding="utf-8") as log_handle:
                log_handle.write(f"\nTIMEOUT after {args.command_timeout} seconds\n")
            status = "FAIL"
            returncode = None
            reason = f"Timed out after {args.command_timeout} seconds"
        result = {
            "index": index,
            "command": command,
            "status": status,
            "returncode": returncode,
            "log": str(log_path.relative_to(ROOT)),
        }
        if reason:
            result["reason"] = reason
        results.append(result)
        print(f"{status:4} {index:02d}: {' '.join(command)}")
        if status == "FAIL" and not args.continue_on_failure:
            break

    failed = [r for r in results if r["status"] == "FAIL"]
    skipped = [r for r in results if r["status"] == "SKIPPED"]
    summary = {
        "mode": mode_name,
        "started": stamp,
        "commandsPlanned": len(commands),
        "stageRange": [args.stage_start, last_stage],
        "partialRun": partial,
        "commandsRun": len(results),
        "passed": sum(r["status"] == "PASS" for r in results),
        "failed": len(failed),
        "skipped": len(skipped),
        "status": "FAIL" if failed else ("PARTIAL_PASS" if partial else "PASS"),
        "results": results,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = [
        f"# Validation run — {mode_name}",
        "",
        f"- Status: **{summary['status']}**",
        f"- Passed: {summary['passed']}",
        f"- Failed: {summary['failed']}",
        f"- Skipped: {summary['skipped']}",
        "",
        "| # | Status | Command |",
        "|---:|:---:|---|",
    ]
    for r in results:
        lines.append(f"| {r['index']} | {r['status']} | `{' '.join(r['command'])}` |")
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "LATEST.txt").write_text(str(run_dir.relative_to(ROOT)) + "\n", encoding="utf-8")
    print(f"Summary: {run_dir.relative_to(ROOT) / 'summary.md'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
