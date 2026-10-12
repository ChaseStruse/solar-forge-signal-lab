#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
export SIGNAL_LAB_UID="$(id -u)"
export SIGNAL_LAB_GID="$(id -g)"
if [[ ! -S "${XDG_RUNTIME_DIR:-}/${WAYLAND_DISPLAY:-}" ]]; then
  echo "Signal Lab needs an active Wayland session." >&2
  exit 1
fi
if [[ ! -S "${XDG_RUNTIME_DIR}/pulse/native" ]]; then
  echo "No PulseAudio-compatible socket found. Start your PipeWire/PulseAudio session first." >&2
  exit 1
fi
exec docker compose up --build -d studio
