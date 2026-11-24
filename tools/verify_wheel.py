from __future__ import annotations

import sys
from pathlib import Path
from zipfile import ZipFile

REQUIRED = {
    "aeng/templates/project/AGENTS.md",
    "aeng/templates/project/CLAUDE.md",
    "aeng/templates/project/agent-instructions/agent-engineering/testing.md",
    "aeng/templates/project/docs/STYLE.md",
    "aeng/templates/project/docs/TRACEABILITY.md",
    "aeng/templates/project/docs/screenshot-index.md",
    "aeng/templates/project/engineering/plans/_TEMPLATE.md",
    "aeng/templates/project/engineering/decisions/_TEMPLATE.md",
    "aeng/templates/project/engineering/manual-tests/_TEMPLATE.md",
    "aeng/templates/project/engineering/verification/test-matrix.yaml",
}


def main() -> int:
    directory = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    wheels = sorted(directory.glob("*.whl"))
    if len(wheels) != 1:
        print(f"Expected exactly one wheel in {directory}, found {len(wheels)}", file=sys.stderr)
        return 2
    with ZipFile(wheels[0]) as archive:
        names = set(archive.namelist())
    missing = sorted(REQUIRED - names)
    if missing:
        print("Wheel is missing required template resources:", file=sys.stderr)
        for name in missing:
            print(f"  {name}", file=sys.stderr)
        return 1
    print(f"Wheel template check passed: {wheels[0].name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
