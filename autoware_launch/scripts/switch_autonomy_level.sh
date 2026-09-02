#!/usr/bin/env bash

set -euo pipefail

SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_NAME="autoware_launch"
LEVEL_FILE="current_level.txt"

usage() {
    cat <<EOF
usage: ${SCRIPT_NAME} <lv2|lv4> [options]
       ${SCRIPT_NAME} --init <lv2|lv4> [options]

Switch the installed ${PKG_NAME} config/launch trees to the given autonomy level.

  <share>/config           -> <share>/config_<level>            (directory symlink)
  <share>/launch/**        -> <levels>/launch_<level>/**        (per-file symlinks)
  <share>/${LEVEL_FILE}    <- "<level>"

<levels> is <share>/../${PKG_NAME}_levels. The launch tree uses per-file symlinks
because ros2launch scans the share directory with os.walk, which neither follows
directory symlinks nor tolerates duplicate launch file names.

options:
  --init             keep the level already configured in <share>; apply the given
                     one only when none is configured yet (used at install time so
                     that a manual switch survives a rebuild)
  --share-dir <path> share directory to operate on (default: auto-detected)
  --dry-run          print what would be done without changing anything
  -q, --quiet        suppress progress messages
  -h, --help         show this help

share directory resolution order:
  1. --share-dir
  2. \$AUTOWARE_LAUNCH_SHARE
  3. <this script>/../../share/${PKG_NAME}   (installed under lib/${PKG_NAME})
  4. ros2 pkg prefix --share ${PKG_NAME}
EOF
}

warn() {
    printf '%s: %s\n' "$SCRIPT_NAME" "$*" >&2
}

die() {
    warn "$*"
    exit 1
}

msg() {
    if [[ $quiet == false ]]; then
        printf '%s: %s\n' "$SCRIPT_NAME" "$*"
    fi
}

run() {
    if [[ $dry_run == true ]]; then
        printf '[dry-run] %s\n' "$*"
    else
        "$@"
    fi
}

is_valid_level() {
    case "$1" in
    lv2 | lv4) return 0 ;;
    *) return 1 ;;
    esac
}

resolve_share_dir() {
    if [[ -n $share_dir_opt ]]; then
        printf '%s\n' "$share_dir_opt"
        return 0
    fi
    if [[ -n ${AUTOWARE_LAUNCH_SHARE:-} ]]; then
        printf '%s\n' "$AUTOWARE_LAUNCH_SHARE"
        return 0
    fi
    local sibling="${SCRIPT_DIR}/../../share/${PKG_NAME}"
    if [[ -d $sibling ]]; then
        printf '%s\n' "$sibling"
        return 0
    fi
    if command -v ros2 >/dev/null 2>&1; then
        local prefix
        if prefix="$(ros2 pkg prefix --share "$PKG_NAME" 2>/dev/null)" && [[ -n $prefix ]]; then
            printf '%s\n' "$prefix"
            return 0
        fi
    fi
    return 1
}

# Echo the level the share directory is currently configured for, based on the
# config symlink (the link is the source of truth, not ${LEVEL_FILE}).
detect_level() {
    local link="$1/config"
    [[ -L $link ]] || return 1
    local target
    target="$(basename "$(readlink "$link")")"
    [[ $target =~ ^config_(lv[0-9]+)$ ]] || return 1
    printf '%s\n' "${BASH_REMATCH[1]}"
}

# The old install layout shipped config/ as a real directory. Left in place it
# shadows config_<level> and silently serves stale parameters, so drop it.
clear_stale_config_dir() {
    local link="$share_dir/config"
    if [[ ! -e $link || -L $link ]]; then
        return 0
    fi
    if [[ -d $link && -d "$share_dir/config_lv4" ]]; then
        warn "'$link' is a real directory left over from the old install layout; recreating it as a symlink"
        run rm -rf "$link"
        return 0
    fi
    die "'$link' exists and is not a symlink; remove it manually (or run: rm -rf build/${PKG_NAME} install/${PKG_NAME})"
}

apply_config() {
    local src="$share_dir/config_$level"
    if [[ ! -d $src ]]; then
        warn "skipping config: $src not found"
        return 1
    fi
    msg "config -> config_$level"
    run ln -sfn "config_$level" "$share_dir/config"
}

apply_launch() {
    local src="$levels_dir/launch_$level"
    local dst="$share_dir/launch"
    if [[ ! -d $src ]]; then
        warn "skipping launch: $src not found"
        return 1
    fi
    msg "launch/** -> launch_$level/** (per-file symlinks)"
    run rm -rf "$dst"
    local path rel dir target last_dir=""
    while IFS= read -r -d '' path; do
        rel="${path#"$src"/}"
        if [[ $rel == */* ]]; then
            dir="$dst/${rel%/*}"
        else
            dir="$dst"
        fi
        if [[ $dir != "$last_dir" ]]; then
            run mkdir -p "$dir"
            last_dir="$dir"
        fi
        # -s keeps the autoware_launch_levels indirection visible in the link
        # target instead of resolving through it (--symlink-install builds make
        # launch_<level> itself a symlink into the source tree).
        target="$(realpath -s --relative-to="$dir" "$path")"
        run ln -sfn "$target" "$dst/$rel"
    done < <(find "$src" -name __pycache__ -prune -o \( -type f -o -type l \) -print0 | sort -z)
}

write_level_file() {
    local file="$share_dir/$LEVEL_FILE"
    if [[ $dry_run == true ]]; then
        printf '[dry-run] write %s <- %s\n' "$file" "$level"
        return 0
    fi
    printf '%s\n' "$level" >"$file"
}

level=""
init_mode=false
share_dir_opt=""
dry_run=false
quiet=false

while (($# > 0)); do
    case "$1" in
    -h | --help)
        usage
        exit 0
        ;;
    --init)
        init_mode=true
        ;;
    --share-dir)
        [[ $# -ge 2 ]] || die "--share-dir requires a path"
        share_dir_opt="$2"
        shift
        ;;
    --dry-run)
        dry_run=true
        ;;
    -q | --quiet)
        quiet=true
        ;;
    -*)
        die "unknown option: $1 (see --help)"
        ;;
    *)
        [[ -z $level ]] || die "level given more than once: $level, $1"
        level="$1"
        ;;
    esac
    shift
done

[[ -n $level ]] || die "missing level; expected lv2 or lv4 (see --help)"
is_valid_level "$level" || die "invalid level: $level (expected lv2 or lv4)"

share_dir="$(resolve_share_dir)" || die "could not locate the ${PKG_NAME} share directory; pass --share-dir"
[[ -d $share_dir ]] || die "share directory not found: $share_dir"
share_dir="$(cd "$share_dir" && pwd)"
levels_dir="$(dirname "$share_dir")/${PKG_NAME}_levels"

if [[ $init_mode == true ]]; then
    if detected="$(detect_level "$share_dir")"; then
        if is_valid_level "$detected"; then
            msg "keeping the configured level: $detected (default was $level)"
            level="$detected"
        else
            warn "unrecognized level '$detected' in the config symlink; falling back to $level"
        fi
    fi
fi

clear_stale_config_dir

applied=0
apply_config && applied=$((applied + 1))
apply_launch && applied=$((applied + 1))

# current_level.txt is written last, so a run that dies halfway leaves the file
# disagreeing with the links and show_autonomy_level.sh reports the mismatch.
if ((applied == 0)); then
    die "nothing to switch: neither config_$level nor launch_$level is installed"
fi
if ((applied < 2)); then
    warn "only part of the tree was switched; the share directory is now inconsistent"
fi
write_level_file
msg "current level: $level"
