# -*- coding: utf-8 -*-
"""Make data/map.json: county outlines for Southeast Michigan, and a position for each ZIP code in the list.

Sources: Census ZCTA gazetteer file; county outlines from the plotly datasets copy of the Census cartographic boundary file.
"""
import csv
import io
import json
import os
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
COUNTIES = {"26163": "Wayne", "26125": "Oakland", "26099": "Macomb", "26161": "Washtenaw", "26093": "Livingston",
            "26115": "Monroe", "26147": "St. Clair", "26091": "Lenawee", "26087": "Lapeer"}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


geo = json.loads(fetch("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"))
shapes = []
for f in geo["features"]:
    if f["id"] in COUNTIES:
        rings = f["geometry"]["coordinates"]
        rings = rings if f["geometry"]["type"] == "Polygon" else [r[0] for r in rings]
        shapes.append({"name": COUNTIES[f["id"]], "rings": [[[round(x, 3), round(y, 3)] for x, y in r] for r in rings]})

z = zipfile.ZipFile(io.BytesIO(fetch("https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_Gaz_zcta_national.zip")))
text = z.read(z.namelist()[0]).decode("utf-8")
pos = {}
for line in text.splitlines()[1:]:
    p = [x.strip() for x in line.split("\t")]
    if p[0][:3] in ("480", "481", "482", "483"):
        pos[p[0]] = [round(float(p[6]), 4), round(float(p[5]), 4)]  # longitude, latitude
with open(os.path.join(HERE, "data", "southeast_michigan_nonprofits.csv"), encoding="utf-8") as f:
    zips = {r["zip"] for r in csv.DictReader(f)}
print(len(shapes), "counties;", len(pos), "ZIP positions;", len(zips - set(pos)), "listed ZIPs with no position")
with open(os.path.join(HERE, "data", "map.json"), "w", encoding="utf-8") as f:
    json.dump({"counties": shapes, "zips": {k: pos[k] for k in zips if k in pos}}, f, separators=(",", ":"))
