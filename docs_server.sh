#!/usr/bin/env bash
# =======================================================================#
# Copyright (C) 2020 - 2026 Dominik Willner <th33xitus@gmail.com>       #
#                                                                       #
# This file is part of KIAUH - Klipper Installation And Update Helper   #
# https://github.com/dw-0/kiauh                                         #
#                                                                       #
# This file may be distributed under the terms of the GNU GPLv3 license #
# =======================================================================#
# Kalico Documentation Server Launcher (Linux/macOS)
# Usage: ./docs_server.sh [port]

PORT="${1:-8800}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

echo "============================================="
echo "  Kalico Documentation Server"
echo "  Port: $PORT"
echo "============================================="
echo ""
echo "Place .md files in:  docs/"
echo "Translations in:     docs/zh/  docs/de/  etc."
echo "   or in:            docs/i18n/simple-chinese/  etc."
echo ""

python3 "$SCRIPT_DIR/docs_server.py" --port "$PORT"
