#!/usr/bin/env bash
# Redraw every Stage 3 picture of partitioning Lab 03, exactly as it was made.
#   bash run_all.sh [teacher clone]        (default: ../../eda-learning-lab3)
# Writes into <clone>/courses/learn_partitioning/module01-03-initial-bipartition/assets/ only.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${1:-$HERE/../../eda-learning-lab3}" && pwd)"
M=courses/learn_partitioning/module01-03-initial-bipartition
S=.cursor/skills/module-slides/scripts
export PYTHONDONTWRITEBYTECODE=1

# 1. numbers from the checker, then the scratch walkthrough viewer
python3 "$HERE/facts.py" "$REPO/$M"
python3 "$HERE/patch_walkthrough.py"

# 2. two local servers: scratch viewer (8081) and the clone's platform (8080, for the lab screenshot)
python3 -m http.server 8081 --bind 127.0.0.1 --directory "$HERE/wt-platform" >/dev/null 2>&1 &
P1=$!
python3 -m http.server 8080 --bind 127.0.0.1 --directory "$REPO/platform" >/dev/null 2>&1 &
P2=$!
trap 'kill $P1 $P2 2>/dev/null' EXIT
for _ in $(seq 20); do
  curl -sf -o /dev/null http://127.0.0.1:8081/ && curl -sf -o /dev/null http://127.0.0.1:8080/ && break
  python3 -c "import time; time.sleep(0.5)"
done

cd "$REPO"
# 3. walkthrough frames + STEPS.md (teacher's script), then put STEPS.md back to CRLF
python3 $S/capture_algorithm_walkthrough.py $M --algo initial-bipartition \
  --base http://127.0.0.1:8081/tools/algorithm-walkthrough
python3 - "$M/assets/STEPS.md" <<'EOF'
import sys
from pathlib import Path
p = Path(sys.argv[1])
t = p.read_text(encoding="utf-8").replace("\r\n", "\n")
p.write_bytes(t.replace("\n", "\r\n").encode("utf-8"))
EOF

# 4. the seven explanation figures
python3 "$HERE/make_figures.py" --module "$M"

# 5. screenshots: the browser lab after a few real actions (Stage 4; the teacher's
#    capture_lab_snapshot.py only loads the page), and a shell running the checker (teacher's script)
python3 "$HERE/capture_lab.py" --module "$M"
python3 $S/capture_real_shell.py $M --example-subdir . \
  --commands "python3 initial_bipartition_check.py | grep PASS | head -14,python3 initial_bipartition_check.py | tail -1"
