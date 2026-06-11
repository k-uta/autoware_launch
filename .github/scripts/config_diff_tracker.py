#!/usr/bin/env python3
"""Generate human-readable markdown diffs between two config directories.

Backend for the ``config-diff`` GitHub Actions workflow. It compares two
directories on a single checkout with a plain file-by-file diff (not ``git
diff``) and writes one markdown file per top-level component (``control``,
``localization``, ...) plus a portal ``README.md`` that lists the differing
files and links each one to its detailed diff.

Paths are resolved relative to ``--base-dir`` (default ``autoware_launch``), so
``config`` means ``autoware_launch/config``. Exits non-zero if either directory
is missing, so the workflow fails on an invalid ``--config-dir-2``.
"""

import argparse
import dataclasses
from datetime import datetime
from datetime import timezone
import difflib
import os
from pathlib import Path
import re
import sys
from typing import Dict
from typing import List
from typing import Set

# File operations, framed as the baseline (a) -> target (b) direction.
OP_ADDED = "added"  # only in dir2 (target)
OP_DELETED = "deleted"  # only in dir1 (baseline)
OP_MODIFIED = "modified"

# Emoji labels, matching the check-config-sync bot.
OP_LABELS = {
    OP_ADDED: "✨ Added",
    OP_DELETED: "🗑️ Deleted",
    OP_MODIFIED: "✏️ Modified",
}

ROOT_COMPONENT = "(root)"  # files directly under the config dir


@dataclasses.dataclass
class FileDiff:
    operation: str
    rel_path: Path  # relative to the config directory
    diff: str  # unified diff text
    anchor: str = ""  # heading anchor in the component markdown


def op_label(operation: str) -> str:
    # Non-breaking space keeps the emoji and label on one line in the table.
    return OP_LABELS.get(operation, operation).replace(" ", "\N{NO-BREAK SPACE}")


def set_output(key: str, value: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return
    with open(github_output, "a") as f:
        if "\n" in value:
            delimiter = "CONFIG_DIFF_EOF"
            f.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
        else:
            f.write(f"{key}={value}\n")


def github_anchor(text: str, seen: Dict[str, int]) -> str:
    """Slugify ``text`` into a GitHub heading anchor, deduplicated via ``seen``.

    Mirrors GitHub: lowercase, drop characters other than word/space/hyphen (so
    ``/`` and ``.`` go, ``_`` stays), spaces to hyphens, and a ``-1``, ``-2``,
    ... suffix on duplicates.
    """
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    count = seen.get(slug, 0)
    seen[slug] = count + 1
    return f"{slug}-{count}" if count else slug


def list_files(root: Path) -> Set[Path]:
    return {path.relative_to(root) for path in root.rglob("*") if path.is_file()}


def read_lines(path: Path) -> List[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)


def component_of(rel_path: Path) -> str:
    return rel_path.parts[0] if len(rel_path.parts) > 1 else ROOT_COMPONENT


def component_filename(component: str) -> str:
    return "root.md" if component == ROOT_COMPONENT else f"{component}.md"


def count_files(components: Dict[str, List[FileDiff]]) -> int:
    return sum(len(entries) for entries in components.values())


def collect_diffs(dir1: Path, dir2: Path, label1: str, label2: str) -> Dict[str, List[FileDiff]]:
    """Compare ``dir1`` and ``dir2`` and group the differing files by component."""
    components: Dict[str, List[FileDiff]] = {}
    for rel in sorted(list_files(dir1) | list_files(dir2)):
        path1, path2 = dir1 / rel, dir2 / rel
        lines1, lines2 = read_lines(path1), read_lines(path2)
        if lines1 == lines2:
            continue

        if not path2.is_file():
            operation = OP_DELETED
        elif not path1.is_file():
            operation = OP_ADDED
        else:
            operation = OP_MODIFIED

        diff = "".join(
            difflib.unified_diff(
                lines1,
                lines2,
                fromfile=f"a/{label1}/{rel.as_posix()}",
                tofile=f"b/{label2}/{rel.as_posix()}",
            )
        )
        components.setdefault(component_of(rel), []).append(FileDiff(operation, rel, diff))

    return components


def assign_anchors(components: Dict[str, List[FileDiff]]) -> None:
    """Set each ``FileDiff.anchor`` within its component's heading namespace."""
    for entries in components.values():
        seen: Dict[str, int] = {}
        for entry in entries:
            entry.anchor = github_anchor(entry.rel_path.as_posix(), seen)


def build_component_markdown(
    component: str, entries: List[FileDiff], label1: str, label2: str
) -> str:
    lines = [
        f"# {component} config diff",
        "",
        f"`{label1}` (a) → `{label2}` (b) · [← portal](README.md)",
        "",
    ]
    for entry in entries:
        lines += [
            f"## {entry.rel_path.as_posix()}",
            "",
            f"**{op_label(entry.operation)}**",
            "",
            "```diff",
            entry.diff.rstrip("\n"),
            "```",
            "",
        ]
    return "\n".join(lines)


def build_portal_markdown(
    components: Dict[str, List[FileDiff]],
    label1: str,
    label2: str,
    timestamp: str,
    source_branch: str = "",
) -> str:
    lines = [
        "# 🔍 Config diff portal",
        "",
        f"`{label1}` (baseline, `a`) → `{label2}` (target, `b`)",
        "",
        f"- generated: {timestamp}",
    ]
    if source_branch:
        lines.append(f"- branch: {source_branch}")
    lines += [
        f"- files with differences: {count_files(components)}",
        "",
    ]

    if not components:
        lines += ["🎉 No differences were found between the two config directories.", ""]
        return "\n".join(lines)

    lines += ["## Summary", "", "| Component | Files with diff |", "| --- | --- |"]
    for component in sorted(components):
        lines.append(
            f"| [{component}]({component_filename(component)}) | {len(components[component])} |"
        )
    lines.append("")

    for component in sorted(components):
        md = component_filename(component)
        lines += [f"## {component}", "", "| Operation | File |", "| --- | --- |"]
        for entry in components[component]:
            link = f"[`{entry.rel_path.as_posix()}`]({md}#{entry.anchor})"
            lines.append(f"| {op_label(entry.operation)} | {link} |")
        lines.append("")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate markdown diffs between two config directories."
    )
    parser.add_argument(
        "--config-dir-1",
        default="config",
        help="baseline config directory, relative to --base-dir (default: config).",
    )
    parser.add_argument(
        "--config-dir-2",
        required=True,
        help="target config directory to compare against, relative to --base-dir.",
    )
    parser.add_argument(
        "--base-dir",
        default="autoware_launch",
        help="directory the config dirs are resolved against (default: autoware_launch).",
    )
    parser.add_argument(
        "--output-dir",
        default="config_diff_output",
        help="directory to write the portal and per-component markdown into.",
    )
    parser.add_argument(
        "--source-branch",
        default="",
        help="branch being compared; shown in the portal when set.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    base = Path(args.base_dir)
    dir1, dir2 = base / args.config_dir_1, base / args.config_dir_2
    for name, directory in (("--config-dir-1", dir1), ("--config-dir-2", dir2)):
        if not directory.is_dir():
            print(f"::error::{name} does not exist: {directory}")
            return 1

    label1, label2 = args.config_dir_1, args.config_dir_2
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    components = collect_diffs(dir1, dir2, label1, label2)
    assign_anchors(components)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for component, entries in components.items():
        (out_dir / component_filename(component)).write_text(
            build_component_markdown(component, entries, label1, label2)
        )
    (out_dir / "README.md").write_text(
        build_portal_markdown(components, label1, label2, timestamp, args.source_branch)
    )

    file_count = count_files(components)
    set_output("status", "diff" if components else "ok")
    set_output("file_count", str(file_count))

    print(f"Compared {dir1} vs {dir2}: {file_count} file(s) with differences.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
