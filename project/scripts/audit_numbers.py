#!/usr/bin/env python3
"""G11 integrity audit: every number in paper/*.md must trace to a value in a result file.

Sources of truth: results/**/*.json, results/**/*.csv, tables/*.md, tables/*.csv, journal_selection/*.md,
literature/reported_results.md (literature numbers, cited as such), results/analysis/*.csv.
A number x with d decimals in the paper matches if some source value v satisfies round(v, d) == x, or
round(100*v, d) == x (percentages), or |v| == |x| for integers. Integers < 10 and numbers inside citation
brackets / DOIs / section numbers are ignored; anything else unmatched fails, unless listed with a reason in
paper/audit_whitelist.txt ("<number> | <reason>").
Usage: python3 scripts/audit_numbers.py [paper/manuscript.md ...]   -> exit 1 on any unmatched number
"""
import csv, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
NUM = re.compile(r"(?<![\w.])[-−]?\d+(?:,\d{3})*(?:\.\d+)?(?![\w])")


def walk(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, out); walk_str(k, out)
    elif isinstance(o, (list, tuple)):
        for v in o:
            walk(v, out)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        out.add(float(o))
    elif isinstance(o, str):
        walk_str(o, out)


def walk_str(s, out):
    for m in NUM.findall(s):
        try:
            out.add(float(m.replace(",", "").replace("−", "-")))
        except ValueError:
            pass


def sources():
    vals = set()
    pats = ["results/**/*.json", "results/**/*.csv", "tables/*.md", "tables/*.csv", "journal_selection/*.md",
            "literature/reported_results.md", "literature/*.csv"]
    for p in pats:
        for f in ROOT.glob(p):
            if "preds" in f.parts:
                continue
            try:
                if f.suffix == ".json":
                    walk(json.loads(f.read_text()), vals)
                else:
                    walk_str(f.read_text(errors="ignore"), vals)
            except Exception:
                pass
    return vals


def matches(x, d, vals):
    for v in vals:
        if round(v, d) == x or round(100 * v, d) == x or (d == 0 and abs(v) == abs(x)):
            return True
    return False


def main():
    files = [Path(a) for a in sys.argv[1:]] or sorted((ROOT / "paper").glob("*.md"))
    wl = {}
    wf = ROOT / "paper/audit_whitelist.txt"
    if wf.exists():
        for line in wf.read_text().splitlines():
            if "|" in line:
                n, r = line.split("|", 1); wl[n.strip()] = r.strip()
    vals = sources()
    bad = []
    for f in files:
        text = f.read_text()
        text = re.sub(r"doi:\S+|https?://\S+|arXiv[: ]\S+|PMC\d+|\[\d+(?:[,–-]\s*\d+)*\]", " ", text)
        for ln, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for m in NUM.findall(line):
                s = m.replace(",", "").replace("−", "-")
                x = float(s); d = len(s.split(".")[1]) if "." in s else 0
                if d == 0 and abs(x) < 10:
                    continue
                if m in wl or s in wl:
                    continue
                if not matches(x, d, vals):
                    bad.append(f"{f.name}:{ln}: {m}  | {line.strip()[:120]}")
    print(f"audit: {len(bad)} unmatched numbers")
    for b in bad[:200]:
        print("  ", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
