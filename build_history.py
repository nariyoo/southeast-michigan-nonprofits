# -*- coding: utf-8 -*-
"""Download revenue and expense history from ProPublica for the 400 largest organizations.

    python build_history.py
Writes data/history.json, which build_design.py puts in the page, since browsers can't call this API directly.
"""
import csv
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "data", "southeast_michigan_nonprofits.csv"), encoding="utf-8") as f:
    rows = sorted(csv.DictReader(f), key=lambda r: -int(r["revenue"]))[:400]
out, failed = {}, 0
for i, r in enumerate(rows, 1):
    url = f"https://projects.propublica.org/nonprofits/api/v2/organizations/{r['ein']}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "workshop-example"})
        with urllib.request.urlopen(req, timeout=40) as x:
            d = json.load(x)
        ys = sorted(((y["tax_prd_yr"], y.get("totrevenue"), y.get("totfuncexpns")) for y in d.get("filings_with_data", [])
                     if y.get("totrevenue") is not None and y.get("totfuncexpns") is not None), key=lambda t: t[0])[-8:]
        if len(ys) >= 2:
            out[r["ein"]] = [list(t) for t in ys]
    except Exception:
        failed += 1
    time.sleep(0.2)
    if i % 100 == 0:
        print(i, "done;", len(out), "with history;", failed, "failed", flush=True)
with open(os.path.join(HERE, "data", "history.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, separators=(",", ":"))
print(len(out), "organizations with history;", failed, "failed")
