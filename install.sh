#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/bin"

if ! command -v python >/dev/null 2>&1; then
    echo "Python is not installed. Run: pkg install python"
    exit 1
fi

python -m pip install flask
cp "$SCRIPT_DIR/sd-server.py" "$HOME/bin/sd-server.py"
cp "$SCRIPT_DIR/pocket-server" "$HOME/bin/pocket-server"
chmod +x "$HOME/bin/pocket-server"

echo
echo "Installed."
echo "Start the server with: ~/bin/pocket-server"
