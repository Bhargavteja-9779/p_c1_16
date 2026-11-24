#!/usr/bin/env python3
"""Verify submission->acceptance times from Crossref 'assertion' metadata (received/accepted).

For each ISSN: fetch journal-articles published in a window (default 12-24 months before
today), parse 'received' and 'accepted' assertions, compute days = accepted - received.
Writes journal_selection/raw/<issn>.json (per-article evidence) and a summary CSV.
Only articles with BOTH dates are used. Nothing is estimated.
"""
import json, sys, time, csv, statistics, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "journal_selection" / "raw"
OUT.mkdir(parents=True, exist_ok=True)
UA = "research-loop-journal-scan/1.0 (python urllib)"

def get(url):
    for a in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(3 * (a + 1))
    raise RuntimeError(url)

def parse_date(s):
    for fmt in ("%d %B %Y", "%d %b %Y", "%Y-%m-%d", "%B %d, %Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except Exception:
            pass
    return None

def scan(issn, start, end, rows=200):
    q = urllib.parse.urlencode({"rows": rows, "filter": f"from-pub-date:{start},until-pub-date:{end},type:journal-article",
                                "select": "DOI,title,assertion,container-title,publisher,published", "sample": rows})
    q = urllib.parse.urlencode({"rows": rows, "filter": f"from-pub-date:{start},until-pub-date:{end},type:journal-article",
                                "select": "DOI,title,assertion,container-title,publisher,published"})
    d = get(f"https://api.crossref.org/journals/{issn}/works?{q}")["message"]
    items = d["items"]
    recs = []
    name = pub = None
    for it in items:
        name = (it.get("container-title") or [name])[0]; pub = it.get("publisher", pub)
        a = {x.get("name"): x.get("value") for x in it.get("assertion", []) if x.get("name") in ("received", "accepted", "revised", "first_online")}
        r, acc = a.get("received"), a.get("accepted")
        if not (r and acc):
            continue
        dr, da = parse_date(r), parse_date(acc)
        if not (dr and da):
            continue
        recs.append({"doi": it["DOI"], "title": (it.get("title") or [""])[0][:150], "received": r,
                     "revised": a.get("revised"), "accepted": acc, "days": (da - dr).days})
    return name, pub, d.get("total-results"), recs

if __name__ == "__main__":
    start, end = sys.argv[1], sys.argv[2]
    issns = sys.argv[3:]
    summ = ROOT / "journal_selection" / "turnaround_summary.csv"
    new = not summ.exists()
    with open(summ, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["issn", "journal", "publisher", "window", "articles_in_window", "n_with_dates", "median_days", "p25", "p75", "min", "max", "share_le_72"])
        for issn in issns:
            try:
                name, pub, tot, recs = scan(issn, start, end)
            except Exception as e:
                print(issn, "ERROR", e); continue
            json.dump({"issn": issn, "journal": name, "publisher": pub, "window": [start, end], "retrieved": datetime.utcnow().isoformat(),
                       "source": f"https://api.crossref.org/journals/{issn}/works", "articles": recs}, open(OUT / f"{issn}.json", "w"), indent=1)
            days = sorted(r["days"] for r in recs)
            if days:
                q = statistics.quantiles(days, n=4) if len(days) > 3 else [days[0], statistics.median(days), days[-1]]
                row = [issn, name, pub, f"{start}..{end}", tot, len(days), statistics.median(days), q[0], q[2], days[0], days[-1], round(sum(x <= 72 for x in days) / len(days), 3)]
            else:
                row = [issn, name, pub, f"{start}..{end}", tot, 0, "", "", "", "", "", ""]
            w.writerow(row); f.flush()
            print(row)
            time.sleep(1)
