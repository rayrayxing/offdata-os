from __future__ import annotations

import copy
import fnmatch
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from build_workstream6_canonical_authority import build_records

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "repository" / "canonical-authority-registry.json"
SCHEMA_PATH = ROOT / "schemas" / "canonical-authority-registry.schema.json"
REPORT_PATH = ROOT / "reports" / "workstream6-canonical-authority-evidence.md"
STATUS_FILES = ("README.md","docs/00-START-HERE.md","docs/14-CODEX-KICKOFF.md","docs/19-PHASE-0-VALIDATION-ADDENDUM.md","docs/20-DEVELOPMENT-STATUS.md")


def _json_object(path: Path) -> dict[str, Any]:
    value=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value,dict): raise ValueError(f"{path} must contain a JSON object")
    return value


def _issue_read_order(path: Path) -> list[str]:
    active=False; items=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line=="## Required read order": active=True; continue
        if active and line.startswith("## "): break
        if not active: continue
        match=re.match(r"^\d+\. `([^`]+)`$",line)
        if match: items.append(match.group(1))
    if not items: raise ValueError("canonical issue body has no parseable required read order")
    return items


def _machine_read_order(path: Path) -> list[str]:
    value=_json_object(path).get("read_order")
    if not isinstance(value,list) or not all(isinstance(item,str) for item in value): raise ValueError("machine handoff read order is invalid")
    return list(value)


def _exact_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result={}
    for record in registry.get("exact_records",[]):
        if isinstance(record,dict) and isinstance(record.get("path"),str): result[record["path"]]=record
    return result


def _classify(registry: dict[str, Any], relative: str) -> dict[str, Any] | None:
    exact=_exact_map(registry).get(relative)
    if exact is not None: return exact
    matches=[rule for rule in registry.get("classification_rules",[]) if isinstance(rule,dict) and fnmatch.fnmatchcase(relative,str(rule.get("pattern","")))]
    if not matches: return None
    highest=max(int(item.get("priority",-1)) for item in matches)
    winners=[item for item in matches if int(item.get("priority",-1))==highest]
    if len({str(item.get("classification")) for item in winners})!=1: return {"classification":"__CONFLICT__","matches":winners}
    return winners[0]


def _all_scanned_paths(registry: dict[str, Any]) -> list[str]:
    result=set()
    for root_name in registry.get("scan_roots",[]):
        root=ROOT/str(root_name)
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file(): result.add(path.relative_to(ROOT).as_posix())
    return sorted(result)


def _semantic_failures(registry: dict[str, Any]) -> list[str]:
    failures=[]
    def require(condition: bool, message: str) -> None:
        if not condition: failures.append(message)
    require(registry.get("work_package_id")=="WS6.4","work package is not WS6.4")
    require(registry.get("base_main_sha")=="be83de22a1178ad9fb5c814d993a0ade8a54f53c","exact WS6.3 base is missing")
    exact=registry.get("exact_records",[]); rules=registry.get("classification_rules",[]); external=registry.get("external_records",[])
    require(isinstance(exact,list) and len(exact)==43,"exact record count is invalid")
    require(isinstance(rules,list) and len(rules)==11,"classification rule count is invalid")
    require(isinstance(external,list) and len(external)==3,"external record count is invalid")
    exact_paths=[item.get("path") for item in exact if isinstance(item,dict)]
    require(len(exact_paths)==len(set(exact_paths)),"exact record paths are not unique")
    rule_ids=[item.get("id") for item in rules if isinstance(item,dict)]; rule_patterns=[item.get("pattern") for item in rules if isinstance(item,dict)]
    require(len(rule_ids)==len(set(rule_ids)),"classification rule ids are not unique")
    require(len(rule_patterns)==len(set(rule_patterns)),"classification rule patterns are not unique")
    counts=Counter(str(item.get("classification")) for item in [*exact,*external] if isinstance(item,dict))
    constraints=registry.get("uniqueness_constraints",{})
    require(isinstance(constraints,dict),"uniqueness constraints are invalid")
    if isinstance(constraints,dict):
        for classification,expected in constraints.items(): require(counts[str(classification)]==expected,f"uniqueness constraint failed for {classification}")
    exact_by_path=_exact_map(registry)
    for path in exact_paths:
        if isinstance(path,str): require((ROOT/path).is_file(),f"exact authority path is missing: {path}")
    expected_classes={
      "handoff/codex-phase0-handoff.json":"current_machine_handoff",
      "handoff/codex-phase0-issue-final.md":"current_issue_body",
      "repository/canonical-authority-registry.json":"current_authority_registry",
      "contracts/workstream6-phase-namespace.json":"current_phase_namespace",
      ".github/workflows/workstream6-final-pre-codex.yml":"current_required_workflow",
      "contracts/workstream6-required-workflow-identity.json":"current_required_workflow_identity",
    }
    for path,classification in expected_classes.items(): require(exact_by_path.get(path,{}).get("classification")==classification,f"current classification is invalid: {path}")
    try:
        sources=registry["read_order_sources"]; machine=_machine_read_order(ROOT/sources["machine_handoff"]); issue=_issue_read_order(ROOT/sources["canonical_issue_body"])
    except (KeyError,OSError,TypeError,ValueError) as exc:
        failures.append(f"read-order source failure: {exc}"); machine=[]; issue=[]
    required_exact=[str(item["path"]) for item in exact if isinstance(item,dict) and item.get("read_order_required") is True]
    read_order=sorted(set(machine)|set(issue)|set(required_exact))
    require(len(machine)>=45,"machine read order regressed"); require(len(issue)>=49,"canonical issue read order regressed"); require(len(read_order)>=52,"combined authority read order regressed")
    for relative in read_order:
        require((ROOT/relative).is_file(),f"read-order file is missing: {relative}")
        classification=_classify(registry,relative); require(classification is not None,f"read-order file is unclassified: {relative}")
        if classification is not None: require(classification.get("classification")!="__CONFLICT__",f"read-order classification conflict: {relative}")
    scanned=_all_scanned_paths(registry); require(len(scanned)>=100,"authority and evidence scan is unexpectedly small")
    for relative in scanned:
        classification=_classify(registry,relative); require(classification is not None,f"authority or evidence file is unclassified: {relative}")
        if classification is not None: require(classification.get("classification")!="__CONFLICT__",f"classification conflict: {relative}")
    issue_bodies=sorted((ROOT/"handoff").glob("codex-phase0-issue*.md")); current_issue_bodies=[p for p in issue_bodies if (_classify(registry,p.relative_to(ROOT).as_posix()) or {}).get("classification")=="current_issue_body"]
    require(len(current_issue_bodies)==1,"exactly one current generated issue body is required")
    for path in issue_bodies:
        relative=path.relative_to(ROOT).as_posix(); classification=(_classify(registry,relative) or {}).get("classification")
        if path not in current_issue_bodies: require(classification in {"superseded_issue_body","current_manual_gate_body"},f"non-current issue material lacks supersession classification: {relative}")
    machine_files=sorted((ROOT/"handoff").glob("codex-phase0-handoff*.json")); current_machine_files=[p for p in machine_files if (_classify(registry,p.relative_to(ROOT).as_posix()) or {}).get("classification")=="current_machine_handoff"]
    require(len(current_machine_files)==1,"exactly one current machine handoff is required")
    expected_external={1:("current_actionable_assignment",True,"open"),19:("current_manual_gate",True,"open"),2:("superseded_duplicate",False,"closed")}; external_by_number={item.get("number"):item for item in external if isinstance(item,dict)}
    for number,(classification,current,state) in expected_external.items():
        record=external_by_number.get(number,{}); require(record.get("classification")==classification,f"issue #{number} classification is invalid"); require(record.get("current") is current,f"issue #{number} current flag is invalid"); require(record.get("expected_state")==state,f"issue #{number} expected state is invalid")
    require(external_by_number.get(2,{}).get("state_reason")=="duplicate","issue #2 duplicate reason is missing")
    status=registry.get("canonical_status_phrase"); require(isinstance(status,str) and "WS6.6" in status,"canonical WS6.6 status phrase is invalid")
    if isinstance(status,str):
        for relative in STATUS_FILES:
            text=(ROOT/relative).read_text(encoding="utf-8"); require(status in text,f"canonical WS6.6 status phrase missing: {relative}"); require("codex_start_authorized=false" in text,f"fail-closed status missing: {relative}"); require("repository/canonical-authority-registry.json" in text,f"authority registry missing: {relative}")
    require(registry.get("closed_defects")==["WS6-CONSIST-001","WS6-CONSIST-007"],"closed defect set is invalid")
    require(registry.get("remaining_blocking_defects")==["WS6-BLOCK-006"],"remaining blocker set is invalid")
    completion=registry.get("completion",{})
    for key in ("all_required_prior_components_pass","ws64_complete","all_current_read_order_items_classified","all_evidence_roots_classified"): require(completion.get(key) is True,f"completion flag {key} is false")
    require(completion.get("final_reconciliation_complete") is False,"final reconciliation was claimed early"); require(completion.get("all_blocking_defects_closed") is False,"all blockers were claimed closed early"); require(completion.get("next_permitted_work_package")=="WS6.7","next package is not WS6.7")
    boundaries=registry.get("boundaries",{}); require(boundaries.get("founder_accountability_preserved") is True,"Founder accountability is not preserved")
    for key,value in boundaries.items():
        if key!="founder_accountability_preserved": require(value is False,f"boundary {key} must remain false")
    return failures


def _set(value: dict[str, Any], path: tuple[str,...], replacement: Any) -> None:
    node: Any=value
    for part in path[:-1]: node=node[part]
    node[path[-1]]=replacement


def main() -> None:
    registry=_json_object(REGISTRY_PATH); schema=_json_object(SCHEMA_PATH)
    errors=list(Draft202012Validator(schema).iter_errors(registry))
    if errors: raise SystemExit("WS6.4 schema validation failed:\n- "+"\n- ".join(error.message for error in errors))
    expected,output,report=build_records()
    if registry!=expected or REGISTRY_PATH.read_text(encoding="utf-8")!=output: raise SystemExit("WS6.4 registry is not deterministic")
    if REPORT_PATH.read_text(encoding="utf-8")!=report: raise SystemExit("WS6.4 evidence report is not deterministic")
    failures=_semantic_failures(registry)
    if failures: raise SystemExit("WS6.4 semantic validation failed:\n- "+"\n- ".join(failures))
    cases=[
      (("work_package_id",),"WS6.3"),(("base_main_sha",),"0"*40),(("closed_defects",),["WS6-CONSIST-001"]),(("remaining_blocking_defects",),[]),
      (("completion","all_required_prior_components_pass"),False),(("completion","ws64_complete"),False),(("completion","all_current_read_order_items_classified"),False),(("completion","all_evidence_roots_classified"),False),(("completion","final_reconciliation_complete"),True),(("completion","all_blocking_defects_closed"),True),(("completion","next_permitted_work_package"),"WS6.8"),
      (("boundaries","founder_accountability_preserved"),False),(("boundaries","codex_start_authorized"),True),(("boundaries","phase0_implementation_authorized"),True),(("uniqueness_constraints","current_machine_handoff"),2),(("uniqueness_constraints","current_issue_body"),2),(("uniqueness_constraints","current_required_workflow"),2),(("uniqueness_constraints","current_required_workflow_identity"),2),
    ]
    rejected=0
    for path,replacement in cases:
        mutated=copy.deepcopy(registry); _set(mutated,path,replacement)
        if _semantic_failures(mutated): rejected+=1
        else: raise SystemExit(f"WS6.4 mutation was not rejected: {'.'.join(path)}")
    structural=[]
    duplicate_exact=copy.deepcopy(registry); duplicate_exact["exact_records"].append(copy.deepcopy(duplicate_exact["exact_records"][0])); structural.append(("duplicate exact path",duplicate_exact))
    for missing,label in [("handoff/codex-phase0-handoff.json","missing current handoff"),(".github/workflows/workstream6-final-pre-codex.yml","missing required workflow"),("contracts/workstream6-required-workflow-identity.json","missing workflow identity contract")]:
        mutated=copy.deepcopy(registry); mutated["exact_records"]=[item for item in mutated["exact_records"] if item["path"]!=missing]; structural.append((label,mutated))
    promoted=copy.deepcopy(registry)
    for item in promoted["exact_records"]:
        if item["path"]=="handoff/codex-phase0-issue.md": item["classification"]="current_issue_body"; item["current"]=True
    structural.append(("promoted superseded issue",promoted))
    missing_rule=copy.deepcopy(registry); missing_rule["classification_rules"]=[item for item in missing_rule["classification_rules"] if item["id"]!="reports"]; structural.append(("unclassified reports",missing_rule))
    duplicate_rule=copy.deepcopy(registry); duplicate_rule["classification_rules"].append(copy.deepcopy(duplicate_rule["classification_rules"][0])); structural.append(("duplicate rule",duplicate_rule))
    for label,mutated in structural:
        if _semantic_failures(mutated): rejected+=1
        else: raise SystemExit(f"WS6.4 structural mutation was not rejected: {label}")
    print(f"WS6.4 canonical authority registry successor validation passed: read_order>=52, scanned_files>={len(_all_scanned_paths(registry))}, exact=43, rules=11, external=3, {rejected} mutations rejected, closed_defects=2, remaining_blockers=1, next=WS6.7, codex_start_authorized=false.")

if __name__=="__main__": main()
