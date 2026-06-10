#!/usr/bin/env python3
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

"""
Generate human-readable diffs between two config directories on the same branch.

This is the backend for the `config-diff` GitHub Actions workflow. Unlike
`launch_diff_tracker.py` (which runs `git diff` between two branches of the same
directory), it performs a plain file-by-file diff between two directories on a
single checkout -- the branch the workflow runs on is already the branch being
compared, so there is no branch argument.

It walks both directory trees and writes one markdown file per top-level
component (`control`, `localization`, ... matching the layout under
`autoware_launch/config`) plus a portal `README.md` that lists, per component,
the files that differ and links each one to its detailed diff section.

Paths passed to `--config-dir-1` / `--config-dir-2` are resolved relative to
`--base-dir` (default `autoware_launch`), so `config` means
`autoware_launch/config`. The script exits non-zero if either directory does not
exist, which lets the workflow fail on an invalid `--config-dir-2`.
"""

# Operations framed as the baseline (a) -> target (b) direction.
OP_ADDED = "added"  # present only in dir2 (target)
OP_DELETED = "deleted"  # present only in dir1 (baseline)
OP_MODIFIED = "modified"

# Display labels mirror the check-config-sync bot's design (emoji + label).
OP_LABELS = {
    OP_ADDED: "✨ Added",
    OP_DELETED: "🗑️ Deleted",
    OP_MODIFIED: "✏️ Modified",
}

ROOT_COMPONENT = "(root)"  # pseudo-component for files directly under the config dir


@dataclasses.dataclass
class FileDiff:
    operation: str  # "added", "deleted" or "modified"
    rel_path: Path  # path relative to the config directory
    diff: str  # unified diff text
    anchor: str = ""  # GitHub heading anchor in the component markdown


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
    """Return the GitHub-style heading anchor for `text`, deduplicated via `seen`.

    GitHub lowercases the text, drops characters that are not word characters,
    spaces, or hyphens (so `/` and `.` are removed, `_` is kept), and turns
    spaces into hyphens. Duplicate slugs get an `-1`, `-2`, ... suffix.
    """
    slug = text.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    count = seen.get(slug, 0)
    seen[slug] = count + 1
    return f"{slug}-{count}" if count else slug


def list_files(root: Path) -> Set[Path]:
    return {p.relative_to(root) for p in root.rglob("*") if p.is_file()}


def read_lines(path: Path) -> List[str]:
    if not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)


def component_of(rel_path: Path) -> str:
    parts = rel_path.parts
    return parts[0] if len(parts) > 1 else ROOT_COMPONENT


def component_filename(component: str) -> str:
    return "root.md" if component == ROOT_COMPONENT else f"{component}.md"


def collect_diffs(dir1: Path, dir2: Path, label1: str, label2: str) -> Dict[str, List[FileDiff]]:
    """Compare `dir1` and `dir2` and group differing files by component."""
    all_files = sorted(list_files(dir1) | list_files(dir2))

    components: Dict[str, List[FileDiff]] = {}
    for rel in all_files:
        path1, path2 = dir1 / rel, dir2 / rel
        lines1, lines2 = read_lines(path1), read_lines(path2)
        if lines1 == lines2:
            continue  # identical, nothing to report

        if path1.is_file() and not path2.is_file():
            operation = OP_DELETED
        elif path2.is_file() and not path1.is_file():
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
    """Fill in each FileDiff.anchor using its component's heading namespace."""
    for entries in components.values():
        seen: Dict[str, int] = {}
        for entry in entries:
            entry.anchor = github_anchor(entry.rel_path.as_posix(), seen)


def build_component_markdown(
    component: str, entries: List[FileDiff], label1: str, label2: str, timestamp: str
) -> str:
    lines = [
        f"# {component} config diff",
        "",
        f"- baseline (`a`): `{label1}`",
        f"- target (`b`): `{label2}`",
        f"- generated: {timestamp}",
        "",
        "[← back to portal](README.md)",
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
    components: Dict[str, List[FileDiff]], label1: str, label2: str, timestamp: str
) -> str:
    file_count = sum(len(entries) for entries in components.values())
    lines = [
        "# 🔍 Config diff portal",
        "",
        "This page compares two config directories on the same branch, framed as "
        f"**`{label1}`** (baseline, `a`) → **`{label2}`** (target, `b`).",
        "",
        f"- baseline (`a`): `{label1}`",
        f"- target (`b`): `{label2}`",
        f"- generated: {timestamp}",
        f"- components with differences: {len(components)}",
        f"- files with differences: {file_count}",
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
    lines += [
        "",
        "Each component below lists the files that differ. Click a file to jump to "
        "its detailed diff in the component page.",
        "",
    ]

    for component in sorted(components):
        md = component_filename(component)
        lines += [f"## {component}", "", "| Operation | File |", "| --- | --- |"]
        for entry in components[component]:
            link = f"[`{entry.rel_path.as_posix()}`]({md}#{entry.anchor})"
            lines.append(f"| {op_label(entry.operation)} | {link} |")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
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
        "--label-1",
        default=None,
        help="display label for config dir 1 (default: the --config-dir-1 value).",
    )
    parser.add_argument(
        "--label-2",
        default=None,
        help="display label for config dir 2 (default: the --config-dir-2 value).",
    )
    args = parser.parse_args()

    base = Path(args.base_dir)
    dir1, dir2 = base / args.config_dir_1, base / args.config_dir_2
    for name, directory in (("--config-dir-1", dir1), ("--config-dir-2", dir2)):
        if not directory.is_dir():
            print(f"::error::{name} does not exist: {directory}")
            return 1

    label1 = args.label_1 or args.config_dir_1
    label2 = args.label_2 or args.config_dir_2
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    components = collect_diffs(dir1, dir2, label1, label2)
    assign_anchors(components)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for component, entries in components.items():
        markdown = build_component_markdown(component, entries, label1, label2, timestamp)
        (out_dir / component_filename(component)).write_text(markdown)
    (out_dir / "README.md").write_text(build_portal_markdown(components, label1, label2, timestamp))

    file_count = sum(len(entries) for entries in components.values())
    set_output("status", "diff" if components else "ok")
    set_output("component_count", str(len(components)))
    set_output("file_count", str(file_count))

    print(
        f"Compared {dir1} vs {dir2}: "
        f"{len(components)} component(s), {file_count} file(s) with differences."
    )
    print(f"Output written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
