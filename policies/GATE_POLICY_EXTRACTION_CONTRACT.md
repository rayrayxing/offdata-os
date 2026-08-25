# Gate Policy Extraction Contract

The exact current G0–G10 source is a runtime-local dependency because the owner will provide the VentureOS checkout to Hermes on the Mac.

Hermes must NOT infer gates from this document. It must inspect the actual checkout, tests, migrations and prior audit artifacts and write `state/ventureos-gate-extraction.json` with:

```json
{
  "source_repo": "/absolute/path/to/VentureOS",
  "source_sha": "<git HEAD>",
  "source_dirty": true,
  "extracted_by": "<profile/model>",
  "evidence_refs": ["path:line-or-symbol"],
  "gates": {
    "G0": {
      "purpose": "...",
      "predecessor": null,
      "requirements": {"exact_source_semantics": "..."},
      "min_admissible_by_purpose": {},
      "financial": {"rules": []},
      "forbid_open_blocking_concerns": true,
      "owner_approval": null,
      "authorized_transition": "...",
      "source_refs": ["file:symbol/test"]
    }
  }
}
```

All G0–G10 entries are mandatory. For G3 also write:
- `required_direct_tuple`: all seven fields;
- `allow_url_domain_fallback`: false;
- `research_can_pass`: false;
- `prototype_can_pass`: false;
- `simulation_can_pass`: false;
- `min_direct_buyer_items`: exact source/policy value.

For numeric financial rules use executable shape:

```json
{"financial":{"rules":[{"path":"metrics.gross_margin_pct","op":">=","value":60}]}}
```

Do not silently preserve a known source bug if it contradicts a stricter previously ratified audit invariant. Mark the conflict in `evidence_refs`, create a BLOCKED policy-ratification task, and ask independent Codex to reconcile it.

Then run:

```bash
python scripts/compile_gate_policy.py --input state/ventureos-gate-extraction.json --load-db
```

Codex independently reviews the mapping. Only after owner/Codex ratification run it with `--activate`.
