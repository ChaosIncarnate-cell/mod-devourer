#!/usr/bin/env bash
# Compile-checks mod-devourer (clang -fsyntax-only) against upstream azerothcore-wotlk + mod-playerbots.
# For cloud sessions: no linking, no server, no database. Needs git, cmake, clang and the AzerothCore build
# dependencies (Debian/Ubuntu: libboost-all-dev libmysqlclient-dev libssl-dev libreadline-dev zlib1g-dev
# libbz2-dev).
#
#   tools/syntax-check.sh [work-dir]          (default work dir: /tmp/devourer-upstream)
#   CORE_PATCH=1 tools/syntax-check.sh        also applies core-patch/*.patch before checking
#
# The commits are the ones the owner's local checkout uses (see core-patch/README.md).
set -euo pipefail

CORE_COMMIT=7f12e89ee5f467a50e62eba1d525eac7dc953d03
PB_COMMIT=7bae1b5c58c76a0aa20381155edc08096d1485b2
MODULE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${1:-/tmp/devourer-upstream}"
AC="$WORK/azerothcore-wotlk"
PB="$AC/modules/mod-playerbots"

mkdir -p "$WORK"
if [ ! -d "$AC/.git" ]; then
    git clone --filter=blob:none --no-checkout https://github.com/mod-playerbots/azerothcore-wotlk.git "$AC"
fi
git -C "$AC" checkout -q --force "$CORE_COMMIT"
if [ ! -d "$PB/.git" ]; then
    git clone --filter=blob:none --no-checkout https://github.com/mod-playerbots/mod-playerbots.git "$PB"
fi
git -C "$PB" checkout -q --force "$PB_COMMIT"

if [ "${CORE_PATCH:-0}" = "1" ]; then
    git -C "$AC" apply "$MODULE/core-patch/class-devourer.patch"
    git -C "$PB" apply "$MODULE/core-patch/playerbots-class-devourer.patch"
fi

ln -sfn "$MODULE" "$AC/modules/mod-devourer"
cmake -S "$AC" -B "$AC/build" -DCMAKE_BUILD_TYPE=Release -DTOOLS_BUILD=none -DSCRIPTS=static -DMODULES=static \
      -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DUSE_COREPCH=0 -DUSE_SCRIPTPCH=0 \
      -DBUILD_TESTING=0 > "$WORK/cmake.log"

python3 - "$AC/build/compile_commands.json" <<'EOF'
import json, re, shlex, subprocess, sys
rc = 0
for e in json.load(open(sys.argv[1])):
    if '/modules/mod-devourer/' not in e['file']:
        continue
    cmd = e.get('command') or ' '.join(map(shlex.quote, e['arguments']))
    cmd = re.sub(r' -o \S+', ' ', cmd).replace(' -c ', ' -fsyntax-only -Wall -Wextra -Wno-unused-parameter ')
    r = subprocess.run(cmd, shell=True, cwd=e['directory'], capture_output=True, text=True)
    print(('OK  ' if r.returncode == 0 else 'FAIL'), e['file'].split('/modules/')[-1])
    for line in r.stderr.splitlines():
        if ('error:' in line or 'warning:' in line) and 'mod-devourer' in line:
            print('    ' + line.split('mod-devourer/')[-1])
    rc |= r.returncode
sys.exit(rc)
EOF
