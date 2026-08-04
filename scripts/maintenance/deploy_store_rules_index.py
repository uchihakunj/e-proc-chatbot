"""Rebuild only the CG Store Purchase Rules corpus and vectors after deployment.

Safe for Rocky Linux: it does not start/stop the web application and does not
change any host, port, proxy, or service configuration. Run from the repository
root after pulling the code:

    python scripts/maintenance/deploy_store_rules_index.py
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROMOTE = ROOT / "scripts" / "maintenance" / "promote_store_rules_ocr.py"
REINDEX = ROOT / "scripts" / "maintenance" / "reindex_store_rules.py"


def run(command: list[str], dry_run: bool) -> None:
    print("$", " ".join(command))
    if not dry_run:
        subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Show the exact safe rebuild commands without changing data.")
    args = parser.parse_args()

    run([sys.executable, str(PROMOTE), "--verified-index-only"], args.dry_run)
    run([sys.executable, str(REINDEX)], args.dry_run)
    print("CG Store Rules corpus and vectors are ready." if not args.dry_run
          else "Dry run complete; no files or vectors were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
