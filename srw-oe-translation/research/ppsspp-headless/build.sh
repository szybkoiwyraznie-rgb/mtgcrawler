#!/usr/bin/env bash
# Rebuild a private, experimental PPSSPP software-only headless runner.
# Writes only below the new directory passed as argument; no game data required.
set -euo pipefail
if [ "$#" -ne 1 ]; then echo "Usage: $0 NEW_WORK_DIR" >&2; exit 2; fi
if [ -e "$1" ]; then echo "Refusing existing work directory: $1" >&2; exit 2; fi
mkdir -p "$1"
work=$(cd "$1" && pwd)
here=$(cd "$(dirname "$0")" && pwd)
clone_pin() {
  local url=$1 dir=$2 hash=$3
  git clone --no-checkout "$url" "$dir"
  git -C "$dir" checkout --detach "$hash"
  test "$(git -C "$dir" rev-parse HEAD)" = "$hash"
}
clone_pin https://github.com/hrydgard/ppsspp.git "$work/ppsspp" fa50bb1976065c4f8b1b47af227d367fe9771555
git -C "$work/ppsspp" submodule update --init --recursive
clone_pin https://github.com/KhronosGroup/OpenGL-Registry.git "$work/gl" 6af574a14089ccfee87efe230ebcdd8742859813
clone_pin https://github.com/KhronosGroup/EGL-Registry.git "$work/egl" e964211ff5f7c2bcada786954a16d5b813379395
git -C "$work/ppsspp" apply --unidiff-zero "$here/ppsspp-local.patch"
git -C "$work/ppsspp" apply "$here/offline-input.patch"
git -C "$work/ppsspp" apply "$here/offline-io-trace.patch"
cp "$here/LocalSoftwareOnlyStubs.c" "$work/ppsspp/headless/LocalSoftwareOnlyStubs.c"
cp "$here/OfflineResearch.h" "$work/ppsspp/headless/OfflineResearch.h"
# This build deliberately never links or calls GL; a real libc path satisfies
# upstream's nonempty OPENGL_LIBRARIES fallback without pretending to provide GL.
libc=$(cc -print-file-name=libc.so)
if [ ! -f "$libc" ]; then echo "Cannot locate libc.so with cc" >&2; exit 1; fi
cmake -S "$work/ppsspp" -B "$work/build" \
  -DCMAKE_BUILD_TYPE=Release -DHEADLESS=ON -DHEADLESS_ONLY=ON -DLIBRETRO=OFF \
  -DUSING_GLES2=ON -DUSING_X11_VULKAN=OFF -DUSE_DISCORD=OFF \
  -DOPENGL_LIBRARIES="$libc" \
  -DCMAKE_C_FLAGS="-I\"$work/gl/api\" -I\"$work/egl/api\"" \
  -DCMAKE_CXX_FLAGS="-I\"$work/gl/api\" -I\"$work/egl/api\""
cmake --build "$work/build" --target PPSSPPHeadless -j "${JOBS:-2}"
echo "Built: $work/build/PPSSPPHeadless"
