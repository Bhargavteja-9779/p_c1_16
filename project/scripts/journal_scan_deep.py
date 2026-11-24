#!/usr/bin/env python3
"""Deep turnaround check for shortlisted journals: all articles in window (cursor paging),
with reference-count as a proxy to separate full research articles (>=25 refs) from
letters/correspondence (short). Writes journal_selection/raw/deep_<issn>.json and prints stats."""
import json, sys, time, statistics, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from journal_scan import get, parse_date
ROOT = Path(__file__).resolve().parents[1]
issn, start, end = sys.argv[1:4]
cursor, recs, n_all = "*", [], 0
while True:
    q = urllib.parse.urlencode({"rows": 500, "cursor": cursor, "filter": f"from-pub-date:{start},until-pub-date:{end},type:journal-article",
                                "select": "DOI,title,assertion,references-count,container-title"})
    m = get(f"https://api.crossref.org/journals/{issn}/works?{q}")["message"]
    if not m["items"]:
        break
    for it in m["items"]:
        n_all += 1
        a = {x.get("name"): x.get("value") for x in it.get("assertion", [])}
        dr, da = parse_date(a.get("received") or ""), parse_date(a.get("accepted") or "")
        if dr and da:
            recs.append({"doi": it["DOI"], "title": (it.get("title") or [""])[0][:160], "received": a["received"],
                         "accepted": a["accepted"], "days": (da - dr).days, "refs": it.get("references-count", 0)})
    cursor = m.get("next-cursor")
    time.sleep(1)
def st(xs):
    xs = sorted(xs)
    if not xs: return {}
    q = statistics.quantiles(xs, n=4)
    return {"n": len(xs), "median": statistics.median(xs), "p25": q[0], "p75": q[2], "min": xs[0], "max": xs[-1], "share_le_72": round(sum(x <= 72 for x in xs) / len(xs), 3)}
out = {"issn": issn, "window": [start, end], "retrieved": datetime.now().isoformat(), "source": f"https://api.crossref.org/journals/{issn}/works",
       "articles_in_window": n_all, "all_with_dates": st([r["days"] for r in recs]),
       "full_articles_refs_ge_25": st([r["days"] for r in recs if r["refs"] >= 25]),
       "short_items_refs_lt_25": st([r["days"] for r in recs if r["refs"] < 25]), "articles": recs}
json.dump(out, open(ROOT / "journal_selection" / "raw" / f"deep_{issn}.json", "w"), indent=1)
print(issn, n_all, json.dumps({k: out[k] for k in ("all_with_dates", "full_articles_refs_ge_25", "short_items_refs_lt_25")}))
