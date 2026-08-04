#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest
echo "Install QGIS + UMEP or a supported standalone SOLWEIG implementation separately."
echo "Set AGNIGEO_SOLWEIG_COMMAND to a wrapper accepting --request <json>; see data/raw/README.md."
