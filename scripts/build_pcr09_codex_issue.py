from __future__ import annotations

from pathlib import Path

import build_pcr09_codex_issue_legacy as _legacy

ROOT = Path(__file__).resolve().parents[1]
_legacy.HANDOFF_SOURCE_PATH = ROOT / "handoff" / "codex-phase0-handoff-pcr09.json"

build_codex_issue = _legacy.build_codex_issue
render_issue_markdown = _legacy.render_issue_markdown
main = _legacy.main

__all__ = ["build_codex_issue", "render_issue_markdown", "main"]

if __name__ == "__main__":
    main()
