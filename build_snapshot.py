# -*- coding: utf-8 -*-
"""Download the IRS list of Michigan tax-exempt organizations and build one static page.

    python build_snapshot.py
Keeps 501(c)(3) organizations in Southeast Michigan (ZIP codes 480 to 483) in eight social service fields.
Writes data/southeast_michigan_nonprofits.csv and stages/step2_plain.html. The data are saved in the page.
"""
import csv
import io
import json
import os
import urllib.request
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://www.irs.gov/pub/irs-soi/eo_mi.csv"
FIELDS = {"F": "Mental health", "I": "Crime and legal", "J": "Employment", "K": "Food",
          "L": "Housing", "O": "Youth", "P": "Human services", "R": "Civil rights"}
ZIPS = ("480", "481", "482", "483")


def num(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=120) as r:
    text = r.read().decode("latin-1")
rows = list(csv.DictReader(io.StringIO(text)))
keep = []
for x in rows:
    ntee = (x.get("NTEE_CD") or "").strip()
    # Health care (NTEE E) is left out, as are hospitals and medical groups with no field code or another code
    if any(w in x["NAME"].upper() for w in ("HOSPITAL", "HEALTH SYSTEM", "HEALTHCARE SYSTEM", "MEDICAL GROUP", "MEDICAL CENTER", "HENRY FORD", "TRINITY HEALTH", "PHYSICIAN")):
        continue
    # Many organizations have no field code in the IRS file, including Food Gatherers, so they stay in as "Not classified"
    if x["ZIP"][:3] in ZIPS and x["SUBSECTION"] == "03" and (not ntee or ntee[0] in FIELDS):
        keep.append({"name": x["NAME"].title(), "ein": x["EIN"], "city": x["CITY"].title(), "zip": x["ZIP"][:5],
                     "field": FIELDS[ntee[0]] if ntee else "Not classified", "revenue": num(x["REVENUE_AMT"]), "assets": num(x["ASSET_AMT"]),
                     "since": (x.get("RULING") or "")[:4], "tax_period": x.get("TAX_PERIOD") or ""})
keep.sort(key=lambda o: -o["revenue"])

os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
with open(os.path.join(HERE, "data", "southeast_michigan_nonprofits.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(keep[0]))
    w.writeheader()
    w.writerows(keep)

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Southeast Michigan Nonprofits</title>
<style>
:root{--ink:#17212b;--line:#c9d1d9;--blue:#00274c;--soft:#f3f5f7}
*{box-sizing:border-box}body{margin:0;background:#fff;color:var(--ink);font:16px/1.45 Arial,Helvetica,sans-serif}
main{max-width:1060px;margin:0 auto;padding:26px max(16px,3vw) 40px}h1{font-size:34px;margin:0 0 4px}.sub{margin:0 0 18px}
form{display:flex;flex-wrap:wrap;gap:12px;align-items:end;margin-bottom:12px}label{display:block;font-weight:700;font-size:14px;margin-bottom:3px}
input,select{font:inherit;padding:8px;border:1px solid var(--ink);min-width:220px;max-width:100%;background:#fff}#count{font-weight:700;margin:10px 0}
.bars{display:grid;grid-template-columns:130px 1fr 54px;gap:5px 10px;align-items:center;font-size:14px;margin:0 0 20px}.bars button{all:unset;cursor:pointer;text-decoration:underline}.bars button:focus-visible{outline:2px solid var(--blue)}.bar{height:14px;background:var(--blue)}.c{text-align:right;font-variant-numeric:tabular-nums}
.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:680px}th{text-align:left;border-bottom:2px solid var(--ink);padding:8px;font-size:14px}td{border-bottom:1px solid var(--line);padding:8px}.n{text-align:right;font-variant-numeric:tabular-nums}a{color:#0b5cad}.note{font-size:14px;margin-top:18px}
</style></head><body><main>
<h1>Southeast Michigan Nonprofits</h1><p class="sub">Who works on what, and where. Choose a field or search for your placement.</p>
<div class="bars" id="bars"></div>
<form onsubmit="return false"><div><label for="q">Name or city</label><input id="q" type="search" placeholder="For example, Ypsilanti"></div>
<div><label for="f">Field</label><select id="f"><option value="">All fields</option></select></div></form>
<p id="count" role="status"></p>
<div class="wrap"><table><thead><tr><th>Organization</th><th>City</th><th>Field</th><th>Since</th><th class="n">Revenue</th><th class="n">Assets</th></tr></thead><tbody id="rows"></tbody></table></div>
<p class="note">Source: <a href="https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf">IRS Exempt Organizations Business Master File</a>, Michigan file, saved when this page was built. 501(c)(3) organizations with ZIP codes 480 to 483, without hospitals and medical care organizations. Amounts come from each organization's latest filing on record, and many small organizations report zero. "Since" is the year of the IRS ruling.</p>
</main><script>
const D=__DATA__;
const money=x=>x?'$'+(x>=1e6?(x/1e6).toFixed(1)+'M':Math.round(x/1e3)+'K'):'';
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const counts={};D.forEach(o=>counts[o.field]=(counts[o.field]||0)+1);
const names=Object.keys(counts).sort((a,b)=>counts[b]-counts[a]),max=counts[names[0]];
const q=document.getElementById('q'),f=document.getElementById('f');
f.innerHTML+=names.map(n=>`<option>${esc(n)}</option>`).join('');
document.getElementById('bars').innerHTML=names.map(n=>`<button data-f="${esc(n)}">${esc(n)}</button><div class="bar" style="width:${100*counts[n]/max}%"></div><div class="c">${counts[n].toLocaleString('en-US')}</div>`).join('');
function draw(){const t=q.value.trim().toLowerCase(),R=D.filter(o=>(!f.value||o.field===f.value)&&(!t||(o.name+' '+o.city).toLowerCase().includes(t)));
 document.getElementById('count').textContent=`${R.length.toLocaleString('en-US')} organizations`+(R.length>50?', largest 50 shown':'');
 document.getElementById('rows').innerHTML=R.slice(0,50).map(o=>`<tr><td><a href="https://projects.propublica.org/nonprofits/organizations/${o.ein}">${esc(o.name)}</a></td><td>${esc(o.city)}</td><td>${esc(o.field)}</td><td>${esc(o.since)}</td><td class="n">${money(o.revenue)}</td><td class="n">${money(o.assets)}</td></tr>`).join('')}
q.addEventListener('input',draw);f.addEventListener('change',draw);
document.getElementById('bars').addEventListener('click',e=>{if(e.target.dataset.f){f.value=e.target.dataset.f;draw()}});draw();
</script></body></html>
"""
with open(os.path.join(HERE, "stages", "step2_plain.html"), "w", encoding="utf-8") as f:
    f.write(PAGE.replace("__DATA__", json.dumps(keep, separators=(",", ":")).replace("</", "<\\/")))
print(len(rows), "Michigan rows;", len(keep), "kept")
print(Counter(o["field"] for o in keep).most_common())
print(sorted({o["tax_period"][:4] for o in keep if o["tax_period"]})[-3:])
for n in ("FOOD GATHERERS", "OZONE HOUSE", "ARAB COMMUNITY CENTER", "FOCUS", "SAFEHOUSE"):
    print(n, [(o["name"], o["city"], o["field"], o["revenue"]) for o in keep if n in o["name"].upper()][:2])
print("page KB", os.path.getsize(os.path.join(HERE, "stages", "step2_plain.html")) // 1024)
