#!/usr/bin/env bash

set -euo pipefail

SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_NAME="autoware_launch"
LEVEL_FILE="current_level.txt"

usage() {
    cat <<EOF
usage: ${SCRIPT_NAME} [-v] [--share-dir <path>]

Print the autonomy level the installed ${PKG_NAME} share directory is set to.

Three things carry the level and all three must agree:
  <share>/config                    symlink to config_<level>
  <share>/launch/**                 symlinks into launch_<level>
  <share>/${LEVEL_FILE}             the level as plain text

On agreement the level ("lv2" or "lv4") is printed to stdout and the exit
status is 0. Otherwise the three values are printed to stderr, nothing is
printed to stdout, and the exit status is 1 -- ${LEVEL_FILE} alone is not
trusted, since a switch that dies halfway can leave it stale.

options:
  --share-dir <path> share directory to inspect (default: auto-detected)
  -v, --verbose      also print where each value came from
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

# Echo the level named by the config symlink, or a "<...>" placeholder saying
# why it could not be read.
read_config_level() {
    local link="$share_dir/config"
    if [[ ! -e $link && ! -L $link ]]; then
        printf '<missing>\n'
        return
    fi
    if [[ ! -L $link ]]; then
        printf '<not a symlink>\n'
        return
    fi
    local target
    target="$(basename "$(readlink "$link")")"
    if [[ $target =~ ^config_(lv[0-9]+)$ ]]; then
        printf '%s\n' "${BASH_REMATCH[1]}"
    else
        printf '<unexpected target: %s>\n' "$target"
    fi
}

# Echo the level named by the launch symlinks. Every symlink under launch/ has
# to point into the same launch_<level>, so a half-finished switch is caught.
read_launch_level() {
    local dir="$share_dir/launch"
    if [[ ! -d $dir ]]; then
        printf '<missing>\n'
        return
    fi
    local path target levels=()
    while IFS= read -r -d '' path; do
        target="$(readlink "$path")"
        if [[ $target =~ /launch_(lv[0-9]+)/ ]]; then
            levels+=("${BASH_REMATCH[1]}")
        else
            levels+=("<unexpected target: $target>")
        fi
    done < <(find "$dir" -name __pycache__ -prune -o -type l -print0)
    if ((${#levels[@]} == 0)); then
        printf '<no symlinks>\n'
        return
    fi
    local uniq
    uniq="$(printf '%s\n' "${levels[@]}" | sort -u)"
    if [[ $(printf '%s\n' "$uniq" | wc -l) -ne 1 ]]; then
        printf '<mixed: %s>\n' "$(printf '%s\n' "$uniq" | paste -sd, -)"
        return
    fi
    printf '%s\n' "$uniq"
}

read_level_file() {
    local file="$share_dir/$LEVEL_FILE"
    if [[ ! -f $file ]]; then
        printf '<missing>\n'
        return
    fi
    local content
    content="$(head -n 1 "$file" | tr -d '[:space:]')"
    if [[ -z $content ]]; then
        printf '<empty>\n'
    else
        printf '%s\n' "$content"
    fi
}

report() {
    local stream="$1"
    printf '%-18s %s\n' "config:" "$config_level" >&"$stream"
    if ((launch_link_count > 0)); then
        printf '%-18s %s (%d symlinks)\n' "launch:" "$launch_level" "$launch_link_count" >&"$stream"
    else
        printf '%-18s %s\n' "launch:" "$launch_level" >&"$stream"
    fi
    printf '%-18s %s\n' "${LEVEL_FILE}:" "$level_file_value" >&"$stream"
}

share_dir_opt=""
verbose=false

while (($# > 0)); do
    case "$1" in
    -h | --help)
        usage
        exit 0
        ;;
    --share-dir)
        [[ $# -ge 2 ]] || die "--share-dir requires a path"
        share_dir_opt="$2"
        shift
        ;;
    -v | --verbose)
        verbose=true
        ;;
    *)
        die "unknown argument: $1 (see --help)"
        ;;
    esac
    shift
done

share_dir="$(resolve_share_dir)" || die "could not locate the ${PKG_NAME} share directory; pass --share-dir"
[[ -d $share_dir ]] || die "share directory not found: $share_dir"
share_dir="$(cd "$share_dir" && pwd)"

config_level="$(read_config_level)"
launch_level="$(read_launch_level)"
level_file_value="$(read_level_file)"
launch_link_count=0
if [[ -d "$share_dir/launch" ]]; then
    launch_link_count="$(find "$share_dir/launch" -name __pycache__ -prune -o -type l -print | wc -l)"
fi

if ! [[ $config_level == "$launch_level" && $config_level == "$level_file_value" ]]; then
    warn "inconsistent autonomy level in $share_dir"
    report 2
    exit 1
fi

if [[ $verbose == true ]]; then
    report 1
fi
printf '%s\n' "$config_level"
