#!/usr/bin/env python3
"""Prior-art search helper: queries OpenAlex (title+abstract search) and arXiv, prints hits,
and logs every query + returned works into state/novelty_ledger.json (queries list).
Usage: python scripts/prior_art.py CLAIM_ID "query 1" "query 2" ...
'Opened' papers are logged separately (scripts/prior_art.py open ...) only after reading."""
import json, sys, time, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
LED = ROOT / "state" / "novelty_ledger.json"

def get(url, js=True):
    for a in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "prior-art-search/1.0"}), timeout=60) as r:
                return json.load(r) if js else r.read().decode()
        except Exception:
            time.sleep(3 * (a + 1))
    return None

def abstract(inv):
    if not inv: return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)

def openalex(q, n=12):
    d = get("https://api.openalex.org/works?" + urllib.parse.urlencode({"search": q, "per-page": n, "select": "id,doi,title,publication_year,cited_by_count,abstract_inverted_index,primary_location"}))
    out = []
    for w in (d or {}).get("results", []):
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
        out.append({"src": "openalex", "id": w["id"], "doi": w.get("doi"), "title": w.get("title"), "year": w.get("publication_year"),
                    "cites": w.get("cited_by_count"), "venue": src, "abstract": abstract(w.get("abstract_inverted_index"))[:1500]})
    return (d or {}).get("meta", {}).get("count"), out

def arxiv(q, n=8):
    t = get("http://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": "all:" + q, "max_results": n}), js=False)
    out = []
    if not t: return out
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for e in ET.fromstring(t).findall("a:entry", ns):
        out.append({"src": "arxiv", "id": e.find("a:id", ns).text, "title": " ".join(e.find("a:title", ns).text.split()),
                    "year": e.find("a:published", ns).text[:4], "abstract": " ".join(e.find("a:summary", ns).text.split())[:1500]})
    return out

if __name__ == "__main__":
    led = json.load(open(LED))
    claim = sys.argv[1]
    for q in sys.argv[2:]:
        cnt, oa = openalex(q)
        ax = arxiv(q.replace('"', ''))
        led["queries"].append({"claim": claim, "query": q, "date": datetime.now().isoformat(timespec="seconds"), "openalex_count": cnt,
                               "hits": [{k: h.get(k) for k in ("src", "id", "doi", "title", "year", "venue", "cites")} for h in oa + ax]})
        print(f"\n### [{claim}] {q}  (OpenAlex total {cnt})")
        for h in oa + ax:
            print(f" - {h['year']} | {h.get('cites','')} | {h['title'][:140]} | {h.get('venue') or h['src']} | {h.get('doi') or h['id']}")
        time.sleep(1)
    json.dump(led, open(LED, "w"), indent=1)
