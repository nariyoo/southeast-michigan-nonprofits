# -*- coding: utf-8 -*-
"""Download mission, website, staff size and officer titles from e-filed Form 990s.

    python build_missions.py
Uses the IRS e-file indexes to find each organization's latest return, then the public XML copy kept by GivingTuesday.
Writes data/filings.json, and saves as it goes so it can be restarted. Small organizations that file a 990-N have no such return.
"""
import csv
import html
import io
import json
import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "filings.json")
UA = {"User-Agent": "Mozilla/5.0"}
# Titles that point to a technology role. Part VII lists officers and the highest paid, so this undercounts.
TECH = re.compile(r"\b(CIO|CTO|IT|TECHNOLOGY|INFORMATION|INFORMATICS|DATA|DIGITAL|SYSTEMS)\b")


def get(url, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)


with open(os.path.join(HERE, "data", "southeast_michigan_nonprofits.csv"), encoding="utf-8") as f:
    eins = {r["ein"] for r in csv.DictReader(f)}
latest = {}
for yr in (2023, 2024, 2025, 2026):
    try:
        with get(f"https://apps.irs.gov/pub/epostcard/990/xml/{yr}/index_{yr}.csv", 300) as r:
            for row in csv.DictReader(io.TextIOWrapper(r, encoding="utf-8", errors="ignore")):
                if row["EIN"] in eins and row["RETURN_TYPE"] in ("990", "990EZ", "990PF"):
                    old = latest.get(row["EIN"])
                    if not old or row["TAX_PERIOD"] >= old[0]:
                        latest[row["EIN"]] = (row["TAX_PERIOD"], row["OBJECT_ID"], row["RETURN_TYPE"])
        print(yr, "index read;", len(latest), "organizations", flush=True)
    except Exception as e:
        print(yr, "index skipped:", e, flush=True)

done = {}
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8") as f:
        done = json.load(f)


def clean(x):
    x = html.unescape(re.sub(r"\s+", " ", x or "")).strip()
    return x if x.upper() not in ("", "N/A", "NA", "NONE", "SEE SCHEDULE O") else ""


def first(x, *tags):
    for t in tags:
        m = re.search(rf"<{t}>(.*?)</{t}>", x, re.S)
        if m and clean(m.group(1)):
            return clean(m.group(1))
    return ""


def one(ein):
    period, oid, kind = latest[ein]
    x = get(f"https://gt990datalake-rawdata.s3.amazonaws.com/EfileData/XmlFiles/{oid}_public.xml").read().decode("utf-8", "ignore")
    titles = [clean(t) for t in re.findall(r"<TitleTxt>(.*?)</TitleTxt>", x, re.S)]
    return ein, {"m": first(x, "MissionDesc", "ActivityOrMissionDesc", "PrimaryExemptPurposeTxt")[:420],
                 "w": first(x, "WebsiteAddressTxt", "WebSiteAddressTxt").lower()[:90],
                 "s": first(x, "TotalEmployeeCnt", "EmployeeCnt"), "v": first(x, "TotalVolunteersCnt"), "y": period[:4], "k": kind,
                 "t": sorted({t for t in titles if TECH.search(t.upper())})[:3]}


todo = [e for e in latest if e not in done]
print(len(todo), "to download", flush=True)
failed = 0
with ThreadPoolExecutor(8) as ex:
    for i, fut in enumerate(as_completed([ex.submit(one, e) for e in todo]), 1):
        try:
            e, v = fut.result()
            done[e] = v
        except Exception:
            failed += 1
        if i % 200 == 0:
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(done, f, separators=(",", ":"))
            print(i, "done;", failed, "failed", flush=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(done, f, separators=(",", ":"))
print("finished:", len(done), "organizations;", failed, "failed;", sum(1 for v in done.values() if v["m"]), "with mission;",
      sum(1 for v in done.values() if v["w"]), "with website;", sum(1 for v in done.values() if v["t"]), "with a technology title")
