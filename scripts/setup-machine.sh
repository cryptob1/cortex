#!/usr/bin/env bash
# oflow — set up a NEW machine end to end.
#
# This does the oflow side (install + config). The vault itself syncs via your
# chosen tool (Obsidian Sync / Syncthing / a cloud drive) — oflow just reads &
# writes a plain-Markdown folder and is built to be multi-device-safe.
#
#   bash scripts/setup-machine.sh
set -euo pipefail

REPO="${OFLOW_REPO:-$HOME/code/oflow}"
echo "== oflow: new-machine setup =="

# 1. Repo
if [ ! -d "$REPO/.git" ]; then
  echo "Cloning oflow -> $REPO"
  git clone https://github.com/cryptob1/oflow.git "$REPO"
fi
cd "$REPO"

# 2. Install everything (venv+deps, UI build, hotkeys, launchers, autostart, dream timer)
echo "Running 'make install' (builds the desktop app — a few minutes the first time)…"
make install

# 3. Where does this machine's synced vault live?
echo
read -rp "Path to your synced vault on THIS machine (e.g. ~/Documents/work): " VAULT
VAULT="${VAULT/#\~/$HOME}"
[ -d "$VAULT" ] || echo "! $VAULT not found yet — connect the vault in Obsidian first (or it'll be created on first capture)."

read -rp "Transcription provider [groq/elevenlabs/openai/deepgram] (groq): " PROVIDER
PROVIDER="${PROVIDER:-groq}"
read -rp "API key for $PROVIDER (blank to set later in the app): " APIKEY

# 4. Write ~/.oflow/settings.json (merge — never clobber existing settings)
python3 - "$VAULT" "$PROVIDER" "$APIKEY" <<'PY'
import json, sys, pathlib
vault, provider, key = sys.argv[1:4]
p = pathlib.Path.home()/".oflow"/"settings.json"
p.parent.mkdir(parents=True, exist_ok=True)
s = json.loads(p.read_text()) if p.exists() else {}
s.update({"provider": provider,
          "brainVaultPath": f"{vault}/oflow",   # oflow WRITES captures here
          "brainReadRoot": vault,               # Ask/initiatives READ the whole vault
          "brainGit": False})                   # sync tool handles history, not git
if key:
    s[{"groq":"groqApiKey","elevenlabs":"elevenlabsApiKey",
       "openai":"openaiApiKey","deepgram":"deepgramApiKey"}.get(provider,"groqApiKey")] = key
p.write_text(json.dumps(s, indent=2)+"\n")
print("Wrote", p)
PY

# 5. Restart the backend
systemctl --user restart app-oflow@autostart.service 2>/dev/null || true

cat <<EOF

Done — oflow captures into: $VAULT/oflow

To sync this vault across your machines, pick ONE:
  • Obsidian Sync — open "$VAULT" in Obsidian, enable Sync, and autostart Obsidian (continuous while it runs)
  • Syncthing     — share "$VAULT" between machines (background, free)
  • Cloud drive   — put "$VAULT" in Dropbox/Drive

Then: hold the Copilot key to dictate · Copilot+N note · Copilot+M meeting.
EOF
