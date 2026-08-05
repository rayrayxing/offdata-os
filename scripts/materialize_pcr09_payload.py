from __future__ import annotations

import base64
import hashlib
import io
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = sorted((ROOT / "scripts").glob(".pcr09_payload_*"))
EXPECTED_SHA256 = "e5797e559e5b1937bac42a8925a5d10e912b2058947d8f89d13d63e6820c1497"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one materialization replacement in {path}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main() -> None:
    if len(CHUNKS) != 9:
        raise RuntimeError(f"Expected 9 payload chunks, found {len(CHUNKS)}")
    encoded = "".join(path.read_text(encoding="ascii") for path in CHUNKS)
    archive = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(archive).hexdigest()
    if digest != EXPECTED_SHA256:
        raise RuntimeError(f"PCR-09 payload digest mismatch: {digest}")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as bundle:
        for member in bundle.getmembers():
            target = (ROOT / member.name).resolve()
            if ROOT not in target.parents and target != ROOT:
                raise RuntimeError(f"Unsafe archive member: {member.name}")
        bundle.extractall(ROOT, filter="data")

    replace_once(
        ROOT / "scripts" / "build_pcr09_codex_issue.py",
        '"handoff_and_operating_activation_match": activation == operating_activation,',
        '"handoff_and_operating_activation_match": (\n'
        '            set(operating_activation) < set(activation)\n'
        '            and set(activation) - set(operating_activation) == {"pcr09_merged_to_main"}\n'
        '        ),',
    )
    replace_once(
        ROOT / "docs" / "48-PCR-09-FIRST-CODEX-ISSUE-REWRITE.md",
        "PCR-09 also reconciles PCR-04 and PCR-08 so `pcr09_merged_to_main` becomes a mandatory activation condition before Codex Phase 0 may start.",
        "PCR-09 extends PCR-04 so `pcr09_merged_to_main` becomes a mandatory Codex-start condition. PCR-08 remains unchanged and immutable; its prior operating-control activation set is preserved as a strict subset of the handoff gate.",
    )

    for path in CHUNKS:
        path.unlink()
    (ROOT / ".github" / "workflows" / "pcr09-materialize.yml").unlink()
    Path(__file__).unlink()


if __name__ == "__main__":
    main()
