#!/usr/bin/env python3
"""Traceability: generate qa/testcases.csv from the blueprint + check invariants.

Sources parsed (single source of truth = the blueprint markdown):
  - Appendix A tables      (docs/blueprint/content/12-appendices.md)  -> TC rows
  - §9.12 journey table    (docs/blueprint/content/04-part3.md)       -> J rows
  - §9 feature catalogue   (docs/blueprint/content/04-part3.md)       -> F ids + priorities
  - Chapter 8 UX tables    (docs/blueprint/content/03-part2b.md)      -> UX ids

Modes:
  --emit   write qa/testcases.csv (id, area, binding, verifies, layer, status=planned)
  --check  invariant report: unknown F/UX refs in bindings (fail),
           P0 features without any TC (fail only with --strict)

Usage:
  python3 tools/traceability.py --emit
  python3 tools/traceability.py --check [--strict]
"""
import argparse
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(ROOT, "docs", "blueprint", "content")
OUT_CSV = os.path.join(ROOT, "qa", "testcases.csv")

RANGE_RE = re.compile(r"^(.*?\D)(\d{1,3})\u2026(\d{1,3})$")


def read(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as fh:
        return fh.read()


def section(text, start_marker, end_marker):
    s = text.find(start_marker)
    e = text.find(end_marker, s + 1) if end_marker else len(text)
    if s < 0:
        raise SystemExit("marker not found: %r" % start_marker)
    return text[s:e if e > 0 else len(text)]


def split_row(line):
    cells, cur, in_code = [], [], False
    for ch in line:
        if ch == "`":
            in_code = not in_code
            cur.append(ch)
        elif ch == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur).strip())
    return cells


def expand_case_id(cid):
    m = RANGE_RE.match(cid)
    if not m:
        return [cid]
    prefix, a, b = m.group(1), int(m.group(2)), int(m.group(3))
    width = len(m.group(2))
    return ["%s%0*d" % (prefix, width, i) for i in range(a, b + 1)]


def parse_case_tables(text):
    """TC rows from any markdown tables headed: Case | (Verifies) | (Binding) | (Layer)."""
    rows = []
    for table in re.findall(r"(?:^\|.*\n?)+", text, re.M):
        lines = [ln for ln in table.strip().split("\n") if ln.strip()]
        if len(lines) < 2:
            continue
        header = [c.lower() for c in split_row(lines[0].strip("|"))]
        if not header or header[0] != "case" or "binding" not in header:
            continue
        ib = header.index("binding")
        iv = header.index("verifies") if "verifies" in header else None
        il = header.index("layer") if "layer" in header else None
        for ln in lines[2:]:
            cells = split_row(ln.strip("|"))
            if len(cells) <= max(i for i in (ib, iv, il) if i is not None):
                continue
            for cid in expand_case_id(cells[0]):
                rows.append({
                    "id": cid,
                    "area": cid.split("-")[1] if cid.startswith("TC-") else "JOURNEY",
                    "binding": cells[ib],
                    "verifies": cells[iv] if iv is not None else "",
                    "layer": cells[il] if il is not None else "",
                })
    return rows


def merge(rows):
    """Merge by case id: union bindings, fill verifies/layer when missing."""
    out = {}
    for r in rows:
        k = r["id"]
        if k not in out:
            out[k] = r
            continue
        cur = out[k]
        if r["binding"] and r["binding"] not in cur["binding"]:
            cur["binding"] = (cur["binding"] + "; " + r["binding"]).strip("; ")
        if not cur["verifies"] and r["verifies"]:
            cur["verifies"] = r["verifies"]
        if not cur["layer"] and r["layer"]:
            cur["layer"] = r["layer"]
    return list(out.values())


def parse_appendix_a():
    """TC rows: Appendix A tables + the §20.6 Catalogue-0 table (bindings merged)."""
    appA = section(read("12-appendices.md"), "# Appendix A —", "# Appendix B —")
    s206 = section(read("10-part8.md"), "## 20.6 Catalogue-0", "## 20.7")
    return merge(parse_case_tables(appA) + parse_case_tables(s206))


def parse_journeys():
    text = section(read("04-part3.md"), "## 9.12", "# Chapter 10")
    rows = []
    for m in re.finditer(r"^\| (J-\d{2}) \| (.+?) \| (.+?) \| (.+?) \|", text, re.M):
        rows.append({"id": m.group(1), "area": "JOURNEY", "binding": "§9.12",
                     "verifies": m.group(2), "layer": "L4/L5"})
    return rows


def parse_features():
    text = read("04-part3.md")
    feats = {}
    for m in re.finditer(r"^\| (F-\d{3}) \|.*?\| (P0|P1|P2) \|", text, re.M):
        feats[m.group(1)] = m.group(2)
    return feats


def parse_ux():
    text = read("03-part2b.md")
    return set(re.findall(r"^\| (UX-\d{3}) \|", text, re.M))


def binding_refs(binding):
    """Extract F-xxx / UX-xxx refs, expanding compact forms F-022/23, F-001/8."""
    refs = set()
    for m in re.finditer(r"\bF-(\d{3})(?:/(\d{2,3}))?", binding):
        refs.add("F-%s" % m.group(1))
        if m.group(2):
            refs.add("F-%03d" % int(m.group(2)))
    for m in re.finditer(r"\bUX-(\d{3})(?:/(\d{3}))?", binding):
        refs.add("UX-%s" % m.group(1))
        if m.group(2):
            refs.add("UX-%s" % m.group(2))
    return refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="fail also on P0 features without any test case")
    args = ap.parse_args()

    cases = parse_appendix_a() + parse_journeys()
    feats = parse_features()
    ux = parse_ux()

    if args.emit:
        os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
        with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["case_id", "area", "binding", "verifies", "layer", "status"])
            for c in sorted(cases, key=lambda r: (r["area"], r["id"])):
                w.writerow([c["id"], c["area"], c["binding"], c["verifies"],
                            c["layer"], "planned"])
        areas = {}
        for c in cases:
            areas[c["area"]] = areas.get(c["area"], 0) + 1
        print("EMIT %s: %d cases | by area: %s"
              % (os.path.relpath(OUT_CSV, ROOT), len(cases),
                 ", ".join("%s=%d" % kv for kv in sorted(areas.items()))))

    if args.check:
        problems, warnings = [], []
        known_f = set(feats)
        covered_f = set()
        for c in cases:
            for ref in binding_refs(c["binding"]):
                if ref.startswith("F-"):
                    covered_f.add(ref)
                    if ref not in known_f:
                        problems.append("%s: unknown %s" % (c["id"], ref))
                elif ref not in ux:
                    problems.append("%s: unknown %s" % (c["id"], ref))
        for f, pri in sorted(feats.items()):
            if f not in covered_f:
                (problems if (args.strict and pri == "P0") else warnings).append(
                    "%s (%s) has no test case binding" % (f, pri))
        print("CHECK: %d features (%d P0), %d UX criteria, %d cases"
              % (len(feats), sum(1 for p in feats.values() if p == "P0"), len(ux), len(cases)))
        for p in problems:
            print("VIOLATION:", p)
        for wmsg in warnings:
            print("open-mapping:", wmsg)
        if problems:
            sys.exit(1)
        print("CHECK OK (%d open mappings to close by G4/G5 — tracked, non-blocking in draft)"
              % len(warnings))


if __name__ == "__main__":
    main()
