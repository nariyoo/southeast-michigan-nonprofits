# -*- coding: utf-8 -*-
"""Build the interactive page from the saved data, following the Airbnb DESIGN.md without its logo or name.

    python build_design.py
Design source: github.com/VoltAgent/awesome-design-md, design-md/airbnb/DESIGN.md.
Writes index.html for publishing and artifact_version.html for a Claude artifact.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "data", "map.json"), encoding="utf-8") as f:
    MAP = json.load(f)
with open(os.path.join(HERE, "data", "southeast_michigan_nonprofits.csv"), encoding="utf-8") as f:
    rows = [{"n": r["name"], "e": r["ein"], "c": r["city"], "z": r["zip"], "f": r["field"], "t": r["ntee"], "r": int(r["revenue"]), "a": int(r["assets"]), "s": r["since"]}
            for r in csv.DictReader(f)]

BODY = """<title>Southeast Michigan Nonprofits</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--primary:#ff385c;--primary-active:#e00b41;--ink:#222;--muted:#6a6a6a;--line:#ddd;--soft:#f7f7f7;--canvas:#fff}
*{box-sizing:border-box}body{margin:0;background:var(--canvas);color:var(--ink);font:16px/1.5 Figtree,-apple-system,system-ui,Roboto,'Helvetica Neue',sans-serif}
.gut{padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}.in{max-width:1440px;margin:0 auto}
header{border-bottom:1px solid var(--line);padding-block:16px 0;background:var(--canvas);position:sticky;top:env(safe-area-inset-top,0px);z-index:5}
.brand{font-weight:700;font-size:19px;color:var(--primary);letter-spacing:-.2px;text-align:center}
.search{display:flex;align-items:center;max-width:600px;margin:12px auto 4px;border:1px solid var(--line);border-radius:999px;padding:6px 6px 6px 24px;box-shadow:0 1px 2px rgba(0,0,0,.08),0 4px 12px rgba(0,0,0,.05)}
.search label{display:block;flex:1;min-width:0;font-size:12px;font-weight:700}.search input{display:block;width:100%;border:0;outline:0;font:inherit;font-size:15px;font-weight:400;color:var(--ink);padding:0;background:none}
.search span{width:42px;height:42px;flex:none;border-radius:50%;background:var(--primary);display:grid;place-items:center}.search:focus-within{border-color:var(--ink)}
.cats{display:flex;gap:24px;overflow-x:auto;padding-top:8px;scrollbar-width:none}.cats button{all:unset;cursor:pointer;flex:none;padding:8px 0 11px;font-size:14px;font-weight:500;color:var(--muted);border-bottom:2px solid transparent}
.cats button:hover{color:var(--ink);border-color:var(--line)}.cats button.on{color:var(--ink);border-color:var(--ink);font-weight:600}.cats button:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
.split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,42%);gap:28px;padding-block:22px 40px}.mapbox{position:sticky;top:176px;align-self:start;height:calc(100vh - 200px);min-height:380px;background:#eef3f6;border-radius:14px;overflow:hidden}
#map{width:100%;height:100%;display:block}#map path{fill:#fff;stroke:#b9c6cf;stroke-width:1}#map text.county{font-size:11px;fill:#7b8a94;text-anchor:middle;pointer-events:none}
#map circle{fill:var(--primary);fill-opacity:.72;stroke:#fff;stroke-width:1;cursor:pointer;transition:r .25s}#map circle:hover{fill:var(--primary-active);fill-opacity:1}#map circle.on{fill:var(--ink);fill-opacity:1}#map circle:focus-visible{outline:none;stroke:var(--ink);stroke-width:2.5}
#tip{position:absolute;left:12px;bottom:12px;background:#fff;border-radius:8px;padding:6px 12px;font-size:14px;font-weight:600;box-shadow:0 2px 8px rgba(0,0,0,.18);max-width:calc(100% - 24px)}
.bar{display:flex;flex-wrap:wrap;gap:10px;justify-content:space-between;align-items:center;margin-bottom:16px}h1{font-size:22px;font-weight:600;letter-spacing:-.3px;margin:0;text-wrap:balance}.tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
select{max-width:210px}select,.chip{font:inherit;font-size:14px;font-weight:500;color:var(--ink);padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--canvas)}.chip{cursor:pointer;background:var(--ink);color:#fff;border-color:var(--ink)}
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:22px 18px}
.card{all:unset;display:flex;flex-direction:column;cursor:pointer;min-width:0}.card:focus-visible .tile{outline:2px solid var(--ink);outline-offset:2px}
.tile{aspect-ratio:16/10;border-radius:14px;padding:14px;display:flex;flex-direction:column;justify-content:space-between;transition:transform .15s,box-shadow .15s}.card:hover .tile{transform:translateY(-2px);box-shadow:0 6px 16px rgba(0,0,0,.12)}
.tag{align-self:flex-start;background:var(--canvas);border-radius:999px;padding:3px 10px;font-size:12px;font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.12)}
.amt{font-size:27px;font-weight:700;letter-spacing:-.5px;font-variant-numeric:tabular-nums;line-height:1.15}.amt.none{font-size:15px;font-weight:500;color:var(--muted);letter-spacing:0}.amt small{display:block;font-size:12px;font-weight:400;color:#555;letter-spacing:0}
.name{font-weight:600;margin-top:9px;line-height:1.3;overflow-wrap:anywhere}.meta{font-size:14px;color:var(--muted)}
#more[hidden]{display:none}#more{display:block;margin:28px auto 0;font:inherit;font-weight:600;padding:11px 24px;border:0;border-radius:8px;background:var(--primary);color:#fff;cursor:pointer}#more:hover{background:var(--primary-active)}
.note{border-top:1px solid var(--line);margin-top:34px;padding-top:14px;font-size:13px;color:var(--muted)}.note a{color:inherit}
dialog{border:0;border-radius:20px;padding:26px;width:min(480px,calc(100vw - 32px));box-shadow:0 12px 40px rgba(0,0,0,.28);color:var(--ink)}dialog::backdrop{background:rgba(0,0,0,.45)}
dialog h2{font-size:24px;line-height:1.2;margin:8px 34px 2px 0;letter-spacing:-.3px;overflow-wrap:anywhere}#close{all:unset;cursor:pointer;position:absolute;top:18px;right:18px;width:32px;height:32px;border-radius:50%;text-align:center;line-height:32px;background:var(--soft);font-size:18px}#close:focus-visible{outline:2px solid var(--ink)}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}.stats div{background:var(--soft);border-radius:12px;padding:12px}.stats b{display:block;font-size:20px;font-variant-numeric:tabular-nums}.stats span{font-size:13px;color:var(--muted)}
.rank{margin:0 0 6px;font-size:15px}.track{height:8px;border-radius:99px;background:#eee;overflow:hidden;margin-bottom:16px}.track i{display:block;height:100%;background:var(--primary)}.link{display:inline-block;background:var(--primary);color:#fff;font-weight:600;text-decoration:none;padding:11px 20px;border-radius:8px}
@media(max-width:860px){.split{grid-template-columns:1fr}.mapbox{position:relative;top:0;height:300px;min-height:0;order:-1}header{position:static}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
<header class="gut"><div class="in"><div class="brand">Southeast Michigan Nonprofits</div>
<div class="search"><label for="q">Name or city<input id="q" type="search" placeholder="Try Ypsilanti, or your placement" autocomplete="off"></label><span aria-hidden="true"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="#fff" stroke-width="2.4"><circle cx="7" cy="7" r="5"/><path d="M11 11l4 4"/></svg></span></div>
<nav class="cats" id="cats" aria-label="Fields"></nav></div></header>
<main class="gut"><div class="in split"><div><div class="bar"><h1 id="count" role="status"></h1><div class="tools"><button id="cityChip" class="chip" type="button" hidden></button><select id="budget" aria-label="Budget size"><option value="">Any budget</option><option value="0">None reported</option><option value="1">Under $100K</option><option value="2">$100K to $1M</option><option value="3">$1M to $10M</option><option value="4">Over $10M</option></select><select id="ntee" aria-label="Type of organization"><option value="">Any type</option></select><select id="era" aria-label="Founded"><option value="">Any year</option><option value="0">Before 1980</option><option value="1">1980 to 1999</option><option value="2">2000 to 2014</option><option value="3">2015 or later</option></select><select id="sort" aria-label="Sort by"><option value="r">Largest revenue</option><option value="a">Largest assets</option><option value="s">Newest</option><option value="n">Name</option></select></div></div>
<div id="grid"></div><button id="more" type="button">Show more</button>
<p class="note">Source: <a href="https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf">IRS Exempt Organizations Business Master File</a>, Michigan file, saved when this page was built. 501(c)(3) organizations with ZIP codes 480 to 483, without hospitals and medical care organizations. Revenue comes from each organization's latest filing on record, so years differ, and many small organizations report zero. "Since" is the year of the IRS ruling. Map positions are ZIP code centers from the Census Bureau.</p></div>
<div class="mapbox"><svg id="map" role="group" aria-label="Map of organizations by city"></svg><div id="tip">Select a circle to filter by city</div></div></div></main>
<dialog id="dlg" aria-labelledby="dName"><button id="close" type="button" aria-label="Close">&times;</button><div id="dBody"></div></dialog>
<script>
const D=__DATA__,M=__MAP__;
const TINT={'Human services':'#fde8ec','Youth':'#fff1d6','Housing':'#e3f1ee','Mental health':'#efe7fb','Food':'#eaf4dc','Crime and legal':'#ece9e4','Employment':'#e2f2f8','Civil rights':'#fbe6da','Not classified':'#f2f2f2'};
const money=x=>x>=1e6?'$'+(x/1e6).toFixed(1)+'M':x>=1e3?'$'+Math.round(x/1e3)+'K':x>0?'$'+x:'None reported';
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const $=i=>document.getElementById(i),counts={};D.forEach(o=>counts[o.f]=(counts[o.f]||0)+1);
const fields=['All',...Object.keys(counts).filter(k=>k!=='Not classified').sort((a,b)=>counts[b]-counts[a]),'Not classified'];
let field='All',city='',shown=24;
$('cats').innerHTML=fields.map(n=>`<button type="button" data-f="${esc(n)}" class="${n==='All'?'on':''}">${esc(n)}</button>`).join('');
// Map: county outlines and one circle per city, placed at the mean of its ZIP centers
const pts=M.counties.flatMap(c=>c.rings.flat()),X=pts.map(p=>p[0]),Y=pts.map(p=>p[1]),x0=Math.min(...X),x1=Math.max(...X),y0=Math.min(...Y),y1=Math.max(...Y),K=Math.cos((y0+y1)/2*Math.PI/180),W=600,H=Math.round(W*(y1-y0)/((x1-x0)*K));
const px=([a,b])=>[+((a-x0)/(x1-x0)*W).toFixed(1),+((y1-b)/(y1-y0)*H).toFixed(1)];
const cityPos={};D.forEach(o=>{const p=M.zips[o.z];if(!p)return;const c=cityPos[o.c]||(cityPos[o.c]={x:0,y:0,n:0});c.x+=p[0];c.y+=p[1];c.n++});
let svg=M.counties.map(c=>{const d=c.rings.map(r=>'M'+r.map(p=>px(p).join(',')).join('L')+'Z').join('');return `<path d="${d}"/>`}).join('');
svg+=M.counties.map(c=>{const r=c.rings[0],a=px([r.reduce((s,p)=>s+p[0],0)/r.length,r.reduce((s,p)=>s+p[1],0)/r.length]);return `<text class="county" x="${a[0]}" y="${a[1]}">${c.name}</text>`}).join('');
svg+=Object.entries(cityPos).sort((a,b)=>b[1].n-a[1].n).map(([n,c])=>{const a=px([c.x/c.n,c.y/c.n]);return `<circle data-c="${esc(n)}" cx="${a[0]}" cy="${a[1]}" r="3" tabindex="0" role="button" aria-label="${esc(n)}"></circle>`}).join('');
$('map').setAttribute('viewBox',`0 0 ${W} ${H}`);$('map').innerHTML=svg;
const NTEE={P20:'Human service organizations',P21:'Human service organizations',P30:'Children and youth services',P31:'Adoption',P32:'Foster care',P33:'Child day care',P40:'Family services',P42:'Single parent agencies',P43:'Family violence shelters',P44:'Homemaker and home health aide',P46:'Family counseling',P50:'Personal social services',P51:'Financial counseling',P52:'Transportation assistance',P60:'Emergency assistance',P61:'Travelers aid',P62:'Victims services',P70:'Residential care',P72:'Half-way houses',P73:'Group homes',P74:'Hospice',P75:'Senior continuing care',P80:'Services for independence',P81:'Senior centers',P82:'Developmental disabilities',P83:'Women centers',P84:'Ethnic and immigrant services',P85:'Homeless services',P86:'Blind and visually impaired',P87:'Deaf and hard of hearing',P99:'Other human services',L20:'Housing development',L21:'Low-income housing',L22:'Senior housing',L25:'Housing rehabilitation',L30:'Housing search assistance',L40:'Temporary housing',L41:'Homeless shelters',L50:'Housing owners and renters',L80:'Housing support',L81:'Home improvement',L82:'Housing expense reduction',L99:'Other housing',K20:'Agricultural programs',K30:'Food programs',K31:'Food banks and pantries',K34:'Congregate meals',K35:'Soup kitchens',K36:'Meals on wheels',K40:'Nutrition programs',K99:'Other food programs',F20:'Substance use prevention and treatment',F21:'Substance use prevention',F22:'Substance use treatment',F30:'Mental health treatment',F31:'Psychiatric hospitals',F32:'Community mental health centers',F33:'Residential mental health',F40:'Hot lines and crisis intervention',F42:'Rape victim services',F50:'Addictive disorders',F52:'Smoking addiction',F53:'Eating disorders',F54:'Gambling addiction',F60:'Counseling',F70:'Mental health disorders',F80:'Mental health associations',F99:'Other mental health',O20:'Youth centers and clubs',O21:'Boys clubs',O22:'Girls clubs',O23:'Boys and girls clubs',O30:'Adult and child matching programs',O31:'Big Brothers and Big Sisters',O40:'Scouting',O41:'Boy Scouts',O42:'Girl Scouts',O50:'Youth development programs',O51:'Youth community service',O52:'Youth agricultural development',O53:'Youth business development',O54:'Youth citizenship',O55:'Youth religious leadership',O99:'Other youth development',I20:'Crime prevention',I21:'Delinquency prevention',I23:'Drunk driving prevention',I30:'Correctional facilities',I31:'Transitional care',I40:'Rehabilitation of offenders',I43:'Inmate support',I44:'Prison alternatives',I50:'Administration of justice',I51:'Dispute resolution',I60:'Law enforcement',I70:'Violence prevention',I71:'Spouse abuse prevention',I72:'Child abuse prevention',I73:'Sexual abuse prevention',I80:'Legal services',I83:'Public interest law',I99:'Other crime and legal',J20:'Employment preparation',J21:'Vocational counseling',J22:'Job training',J30:'Vocational rehabilitation',J32:'Goodwill Industries',J33:'Sheltered employment',J40:'Labor unions',J99:'Other employment',R20:'Civil rights',R22:'Minority rights',R23:'Disabled rights',R24:'Women rights',R25:'Senior rights',R26:'LGBTQ rights',R30:'Intergroup relations',R40:'Voter education',R60:'Civil liberties',R61:'Reproductive rights',R62:'Right to life',R63:'Censorship and free speech',R67:'Right to die',R99:'Other civil rights'};
const nteeName=c=>(NTEE[c]||NTEE[c[0]+c[1]+'0']||'Other')+' ('+c+')';
const budgetOf=r=>r<=0?'0':r<1e5?'1':r<1e6?'2':r<1e7?'3':'4';
const eraOf=s=>{const y=+s;return !y?'':y<1980?'0':y<2000?'1':y<2015?'2':'3'};
function fillNtee(){const c={};D.forEach(o=>{if(o.t&&(field==='All'||o.f===field))c[o.t]=(c[o.t]||0)+1});const keep=$('ntee').value;
 $('ntee').innerHTML='<option value="">Any type</option>'+Object.entries(c).sort((a,b)=>b[1]-a[1]).map(([k,n])=>`<option value="${k}">${esc(nteeName(k))}: ${n}</option>`).join('');$('ntee').value=c[keep]?keep:''}
function base(){const b=$('budget').value,t=$('ntee').value,g=$('era').value;return D.filter(o=>(field==='All'||o.f===field)&&(!b||budgetOf(o.r)===b)&&(!t||o.t===t)&&(!g||eraOf(o.s)===g))}
function list(){const t=$('q').value.trim().toLowerCase(),k=$('sort').value,R=base().filter(o=>(!city||o.c===city)&&(!t||(o.n+' '+o.c).toLowerCase().includes(t)));
 return R.sort((a,b)=>k==='n'?a.n.localeCompare(b.n):k==='s'?(b.s||'').localeCompare(a.s||''):b[k]-a[k])}
function paintMap(){const c={};base().forEach(o=>c[o.c]=(c[o.c]||0)+1);
 document.querySelectorAll('#map circle').forEach(e=>{const n=c[e.dataset.c]||0;e.setAttribute('r',n?(3.5+Math.sqrt(n)*.52).toFixed(1):0);e.classList.toggle('on',e.dataset.c===city);e.dataset.n=n})}
function draw(){const R=list(),label=field==='All'?'organizations':field==='Not classified'?'organizations with no field code':field.toLowerCase()+' organizations';
 $('count').textContent=`${R.length.toLocaleString('en-US')} ${R.length===1?label.replace('organizations','organization'):label}${city?' in '+city:''}`;
 $('cityChip').hidden=!city;$('cityChip').textContent=city+'  \\u00d7';
 $('grid').innerHTML=R.slice(0,shown).map(o=>`<button class="card" type="button" data-e="${o.e}"><div class="tile" style="background:${TINT[o.f]}"><span class="tag">${esc(o.f)}</span><div class="amt${o.r?'':' none'}">${money(o.r)}${o.r?'<small>latest revenue</small>':''}</div></div><div class="name">${esc(o.n)}</div><div class="meta">${esc(o.c)}${o.s&&o.s!=='0000'?' &middot; since '+esc(o.s):''}</div></button>`).join('')||'<p>Nothing matches. Try another spelling, or the field "Not classified".</p>';
 $('more').hidden=R.length<=shown;paintMap()}
function open(e){const o=D.find(x=>x.e===e),peers=D.filter(x=>x.f===o.f).sort((a,b)=>b.r-a.r),rank=peers.findIndex(x=>x.e===e)+1,pct=o.r?Math.max(2,100*(peers.length-rank+1)/peers.length):0;
 $('dBody').innerHTML=`<span class="tag" style="background:${TINT[o.f]}">${esc(o.t?nteeName(o.t):o.f)}</span><h2 id="dName">${esc(o.n)}</h2><div class="meta">${esc(o.c)}, Michigan ${esc(o.z)}${o.s&&o.s!=='0000'?' &middot; since '+esc(o.s):''}</div>
 <div class="stats"><div><b>${money(o.r)}</b><span>Latest revenue</span></div><div><b>${money(o.a)}</b><span>Assets</span></div></div>
 ${o.r?`<p class="rank">Number ${rank.toLocaleString('en-US')} of ${peers.length.toLocaleString('en-US')} by revenue ${o.f==='Not classified'?'among organizations with no field code':'in '+esc(o.f.toLowerCase())}</p><div class="track"><i style="width:${pct}%"></i></div>`:''}
 <a class="link" href="https://projects.propublica.org/nonprofits/organizations/${o.e}">See filings on ProPublica</a>`;$('dlg').showModal()}
const reset=()=>{shown=24;draw()};
$('q').addEventListener('input',reset);['sort','budget','ntee','era'].forEach(i=>$(i).addEventListener('change',reset));$('more').addEventListener('click',()=>{shown+=24;draw()});
$('cityChip').addEventListener('click',()=>{city='';reset()});
$('cats').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;field=b.dataset.f;document.querySelectorAll('#cats button').forEach(x=>x.classList.toggle('on',x===b));fillNtee();reset()});
$('grid').addEventListener('click',e=>{const c=e.target.closest('.card');if(c)open(c.dataset.e)});
$('close').addEventListener('click',()=>$('dlg').close());$('dlg').addEventListener('click',e=>{if(e.target===$('dlg'))$('dlg').close()});
const pick=e=>{const c=e.target.closest('circle');if(c){city=city===c.dataset.c?'':c.dataset.c;reset()}};
$('map').addEventListener('click',pick);$('map').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();pick(e)}});
$('map').addEventListener('mouseover',e=>{const c=e.target.closest('circle');if(c)$('tip').textContent=`${c.dataset.c}: ${(+c.dataset.n).toLocaleString('en-US')} organizations`});
fillNtee();draw();
</script>
"""
data = json.dumps(rows, separators=(",", ":")).replace("</", "<\\/")
body = BODY.replace("__DATA__", data).replace("__MAP__", json.dumps(MAP, separators=(",", ":")))
with open(os.path.join(HERE, "artifact_version.html"), "w", encoding="utf-8") as f:
    f.write(body)
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
    f.write('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n' + body.replace("</style>\n<header", "</style></head><body>\n<header", 1) + "</body></html>\n")
print(len(rows), "organizations;", os.path.getsize(os.path.join(HERE, "index.html")) // 1024, "KB")
