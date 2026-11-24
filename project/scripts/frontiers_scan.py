#!/usr/bin/env python3
"""Turnaround for Frontiers journals (no dates in Crossref): DOIs from Crossref (window 12-24 months ago),
Received/Accepted parsed from the public article page (plain HTTP GET). Writes journal_selection/raw/frontiers_<issn>.json."""
import json, re, sys, time, statistics, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
issn, n = sys.argv[1], int(sys.argv[2])
q = urllib.parse.urlencode({"rows": n, "filter": "from-pub-date:2024-11-24,until-pub-date:2025-11-24,type:journal-article", "select": "DOI,container-title,references-count", "sample": n})
q = urllib.parse.urlencode({"rows": n, "filter": "from-pub-date:2024-11-24,until-pub-date:2025-11-24,type:journal-article", "select": "DOI,container-title,references-count"})
items = json.load(urllib.request.urlopen(f"https://api.crossref.org/journals/{issn}/works?{q}", timeout=60))["message"]["items"]
recs = []
for it in items:
    try:
        req = urllib.request.Request("https://doi.org/" + it["DOI"], headers={"User-Agent": "Mozilla/5.0"})
        t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
        s = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))
        m = re.search(r"Received (\d{1,2} \w+ \d{4}) Accepted (\d{1,2} \w+ \d{4})", s)
        if m:
            r, a = (datetime.strptime(x, "%d %B %Y") for x in m.groups())
            recs.append({"doi": it["DOI"], "received": m.group(1), "accepted": m.group(2), "days": (a - r).days, "refs": it.get("references-count")})
    except Exception as e:
        pass
    time.sleep(1.5)
d = sorted(r["days"] for r in recs)
name = items[0]["container-title"][0] if items else issn
summ = {"issn": issn, "journal": name, "n": len(d), "median": statistics.median(d) if d else None, "min": d[0] if d else None, "max": d[-1] if d else None,
        "share_le_72": round(sum(x <= 72 for x in d) / len(d), 3) if d else None}
json.dump({"summary": summ, "source": "Crossref DOIs + public article pages", "retrieved": datetime.now().isoformat(), "articles": recs},
          open(ROOT / "journal_selection" / "raw" / f"frontiers_{issn}.json", "w"), indent=1)
print(summ)
