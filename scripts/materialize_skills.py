#!/usr/bin/env python3
"""Materialize OFF/DATA task Skills from the declarative Skill catalogue.
Task Skills are procedural and writable only through the governed Skill Forge workflow.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/"manifests"/"skills.final.json").read_text())
PROFILES=json.loads((ROOT/"manifests"/"profiles.final.json").read_text())

def skill_md(name,spec):
    d=CAT["defaults"]
    def bullets(items): return "\n".join(f"{i+1}. {x}" for i,x in enumerate(items))
    def dash(items): return "\n".join(f"- {x}" for x in items)
    return f"""---
name: {name}
description: {spec['description']}
version: {d['version']}
platforms: [macos, linux]
metadata:
  offdata:
    protected_policy: false
    source_catalogue: OD-SKILLS-0.2-final
---
# {name}

## Purpose
{spec['purpose']}

## Inputs
{dash(spec.get('inputs',[]))}

## Procedure
{bullets(spec.get('procedure',[]))}

## Required output
{spec.get('output','Structured artifact linked from Venture Brain/Kanban.')}

## Quality gates
{dash(spec.get('quality',[]))}

## OFF/DATA global rules
{dash(d['global_rules'])}

## Blocked behavior
If a required source, credential, deterministic tool, authority or material capability is missing, return `BLOCKED` with the exact missing input. Do not improvise authority or synthetic evidence.
"""

def homes():
    for p in PROFILES["profiles"]:
        yield p, Path.home()/".hermes"/"profiles"/p["name"]

def install_external():
    commands=[
      ["hermes","skills","install","mvanhorn/last30days-skill/skills/last30days","--force"],
      ["hermes","skills","install","official/dogfood/adversarial-ux-test"],
      ["hermes","skills","install","official/finance/3-statement-model"]
    ]
    for cmd in commands:
        print("+"," ".join(cmd)); subprocess.run(cmd,check=False)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--skip-external",action="store_true"); ns=ap.parse_args()
    if not ns.skip_external: install_external()
    for profile,home in homes():
        if not home.exists(): continue
        skillroot=home/"skills"/"offdata"; skillroot.mkdir(parents=True,exist_ok=True)
        wanted=set(profile.get("skills",[]))
        # Materialize every custom OFF/DATA Skill needed by this role. Built-in/external names simply remain provided by Hermes.
        for name in sorted(wanted):
            spec=CAT["skills"].get(name)
            if not spec: continue
            dest=skillroot/name; dest.mkdir(parents=True,exist_ok=True); (dest/"SKILL.md").write_text(skill_md(name,spec))
    # Shared mutable learned Skills live separately; bootstrap points Skill Forge there but never overwrites certified built-ins.
    learned=Path.home()/".offdata"/"skills"/"learned"; learned.mkdir(parents=True,exist_ok=True)
    print(f"OFF/DATA custom Skills materialized. Mutable learned Skill root: {learned}")

if __name__=="__main__": main()
