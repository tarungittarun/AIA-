#!/usr/bin/env python3
"""OneDoc traceability — parse the blueprint catalogues, emit qa/onedoc/testcases.csv,
and check the invariants (§4.1, §29.5):

  * every feature F-nnn has >= 1 test-case binding
  * every P0 feature has >= 1 binding (enforced by --strict)
  * every UX-nnn has >= 1 binding
  * every binding resolves to a case in the catalogue (Appendix C)
  * the run manifest (Appendix U) covers exactly the catalogue

Usage:
  traceability.py --emit             # regenerate qa/onedoc/testcases.csv
  traceability.py --check [--strict] # verify invariants; exit 0 = green
"""
import argparse
import csv
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTENT = os.path.join(ROOT, "docs", "onedoc", "blueprint", "content")
CSV_OUT = os.path.join(ROOT, "qa", "onedoc", "testcases.csv")

FEAT_RE = re.compile(r"^\|\s*(F-\d+)\s*\|\s*([^|]+?)\s*\|\s*(P\d)\s*\|\s*([^|]+?)\s*\|\s*$")
UX_RE = re.compile(r"^\|\s*(UX-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")
CASE_RE = re.compile(r"^\|\s*(TC-[A-Z0-9]+(?:-[A-Z0-9]+)+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def parse_features():
    feats = {}
    for line in read(os.path.join(CONTENT, "14-appendix-a.md")).splitlines():
        m = FEAT_RE.match(line)
        if m and m.group(1) != "F-id":
            fid, name, pri, binds = m.groups()
            feats[fid] = {"name": name, "priority": pri,
                          "bindings": [b.strip() for b in binds.split(",") if b.strip()]}
    return feats


def parse_ux():
    uxs = {}
    started = False
    for line in read(os.path.join(CONTENT, "14-appendix-a.md")).splitlines():
        if line.startswith("| UX-id"):
            started = True
            continue
        if started:
            m = UX_RE.match(line)
            if m and m.group(1) != "UX-id":
                uid, crit, binds = m.groups()
                uxs[uid] = {"criterion": crit,
                            "bindings": [b.strip() for b in binds.split(",") if b.strip()]}
            elif line.strip() and not line.startswith("|"):
                started = False
    return uxs


def parse_cases():
    """Case rows live in Appendix C (15-appendix-b.md, 16-appendix-c.md)."""
    cases = {}
    for path in ("15-appendix-b.md", "16-appendix-c.md"):
        for line in read(os.path.join(CONTENT, path)).splitlines():
            m = CASE_RE.match(line)
            if m and m.group(1) != "Case":
                cid, binds, proves, level = m.groups()
                area = cid[3:cid.rfind("-")]
                entry = cases.setdefault(cid, {"bindings": set(), "proves": [], "level": set(), "area": area})
                entry["bindings"].update(b.strip() for b in binds.split(",") if b.strip())
                if proves.strip() and proves.strip() not in entry["proves"]:
                    entry["proves"].append(proves.strip())
                entry["level"].add(level.strip())
    return cases


def parse_manifest():
    ids = []
    for line in read(os.path.join(CONTENT, "25-appendix-u.md")).splitlines():
        m = re.match(r"^\|\s*(TC-[A-Z0-9]+(?:-[A-Z0-9]+)+)\s*\|", line)
        if m and m.group(1) != "Case":
            ids.append(m.group(1))
    return ids


def emit(cases):
    os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
    with open(CSV_OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["case_id", "area", "bindings", "proves", "level"])
        for cid in sorted(cases):
            c = cases[cid]
            w.writerow([cid, c["area"], " ".join(sorted(c["bindings"])),
                        " | ".join(c["proves"]), "/".join(sorted(c["level"]))])
    return sum(1 for _ in cases)


def area_counts(cases):
    counts = {}
    for c in cases.values():
        counts[c["area"]] = counts.get(c["area"], 0) + 1
    return dict(sorted(counts.items()))


def check(feats, uxs, cases, manifest, strict):
    problems = []
    open_map = []
    for fid, f in sorted(feats.items()):
        resolved = [b for b in f["bindings"] if b in cases]
        if not resolved:
            open_map.append(fid)
            if strict and f["priority"] == "P0":
                problems.append("P0 %s (%s) has no resolvable binding" % (fid, f["name"]))
    for uid, u in sorted(uxs.items()):
        if not [b for b in u["bindings"] if b in cases]:
            open_map.append(uid)
    # dangling bindings (binding names a case that does not exist)
    for fid, f in feats.items():
        for b in f["bindings"]:
            if b not in cases:
                problems.append("%s -> unresolvable case %s" % (fid, b))
    for uid, u in uxs.items():
        for b in u["bindings"]:
            if b not in cases:
                problems.append("%s -> unresolvable case %s" % (uid, b))
    # manifest equality
    extra = [c for c in manifest if c not in cases]
    missing = [c for c in sorted(cases) if c not in manifest]
    if extra:
        problems.append("manifest lists %d case(s) not in catalogue: %s" % (len(extra), extra[:5]))
    if missing:
        problems.append("manifest missing %d catalogue case(s): %s" % (len(missing), missing[:5]))
    p0 = sum(1 for f in feats.values() if f["priority"] == "P0")
    print("CHECK: %d features (%d P0), %d UX criteria, %d cases"
          % (len(feats), p0, len(uxs), len(cases)))
    print("areas:", ", ".join("%s=%d" % kv for kv in area_counts(cases).items()))
    if open_map:
        print("open mappings (%d): %s" % (len(open_map), ", ".join(sorted(open_map))))
    else:
        print("open mappings: none")
    for p in problems:
        print("VIOLATION:", p)
    if problems:
        print("CHECK FAILED")
        return 1
    print("CHECK OK (strict=%s)" % strict)
    return 0


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true")
    g.add_argument("--check", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    feats = parse_features()
    uxs = parse_ux()
    cases = parse_cases()
    manifest = parse_manifest()
    if args.emit:
        n = emit(cases)
        print("EMIT %s: %d cases | areas: %s" % (os.path.relpath(CSV_OUT, ROOT), n,
              ", ".join("%s=%d" % kv for kv in area_counts(cases).items())))
        return 0
    return check(feats, uxs, cases, manifest, args.strict)


if __name__ == "__main__":
    sys.exit(main())
