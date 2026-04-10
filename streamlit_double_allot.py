"""
FFCS VIT Chennai — Two-Section Timetable Dashboard
"""

import json
import os
import streamlit as st
import pandas as pd
from collections import defaultdict
from itertools import product
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="VIT Chennai FFCS", layout="wide")

# ══════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    with open("data/two_section_timetable.json") as f:
        data = json.load(f)
    with open("data/recs.json") as f:
        recs = json.load(f)["students"]
    with open("data/courses.json") as f:
        courses_raw = json.load(f)
    course_name_map = {
        c["course_code"]: c["course_name"]
        for c in courses_raw["courses"]
    }
    return data, recs, course_name_map

data, recs, course_name_map = load_data()
timetable        = data["timetable"]
lab_timetable    = data["lab_timetable"]
metrics          = data["metrics"]
student_sections = data["student_sections"]

# ══════════════════════════════════════════════════════════════════
# ENROLMENT COUNTS
# ══════════════════════════════════════════════════════════════════

theory_demand = defaultdict(int)
lab_demand    = defaultdict(int)
for s in recs:
    for c in s["recommended_courses"]:
        if c in timetable:     theory_demand[c] += 1
        if c in lab_timetable: lab_demand[c]    += 1

# ══════════════════════════════════════════════════════════════════
# OVERLAP TABLES
# ══════════════════════════════════════════════════════════════════

@st.cache_data
def build_overlap_tables(_lab_timetable_json):
    lab_timetable_data = json.loads(_lab_timetable_json)
    THEORY_PERIOD_TIMES = {
        1:(480,530),2:(540,590),3:(600,650),4:(660,710),5:(720,770),
        6:(840,890),7:(900,950),8:(960,1010),9:(1020,1070),
        10:(1080,1130),11:(1111,1170)
    }
    LAB_PERIOD_TIMES = {
        "M1":(480,530),"M2":(531,580),"M3":(591,640),"M4":(641,690),
        "M5":(700,750),"M6":(751,810),
        "E1":(840,890),"E2":(891,940),"E3":(951,1000),"E4":(1001,1050),
        "E5":(1060,1110),"E6":(1111,1160),
    }
    LAB_SLOT_MAP = {
        "L1":("MON","M1"),"L2":("MON","M2"),"L3":("MON","M3"),"L4":("MON","M4"),
        "L5":("MON","M5"),"L6":("MON","M6"),
        "L7":("TUE","M1"),"L8":("TUE","M2"),"L9":("TUE","M3"),"L10":("TUE","M4"),
        "L11":("TUE","M5"),"L12":("TUE","M6"),
        "L13":("WED","M1"),"L14":("WED","M2"),"L15":("WED","M3"),"L16":("WED","M4"),
        "L17":("WED","M5"),"L18":("WED","M6"),
        "L19":("THU","M1"),"L20":("THU","M2"),"L21":("THU","M3"),"L22":("THU","M4"),
        "L23":("THU","M5"),"L24":("THU","M6"),
        "L25":("FRI","M1"),"L26":("FRI","M2"),"L27":("FRI","M3"),"L28":("FRI","M4"),
        "L29":("FRI","M5"),"L30":("FRI","M6"),
        "L31":("MON","E1"),"L32":("MON","E2"),"L33":("MON","E3"),"L34":("MON","E4"),
        "L35":("MON","E5"),"L36":("MON","E6"),
        "L37":("TUE","E1"),"L38":("TUE","E2"),"L39":("TUE","E3"),"L40":("TUE","E4"),
        "L41":("TUE","E5"),"L42":("TUE","E6"),
        "L43":("WED","E1"),"L44":("WED","E2"),"L45":("WED","E3"),"L46":("WED","E4"),
        "L47":("WED","E5"),"L48":("WED","E6"),
        "L49":("THU","E1"),"L50":("THU","E2"),"L51":("THU","E3"),"L52":("THU","E4"),
        "L53":("THU","E5"),"L54":("THU","E6"),
        "L55":("FRI","E1"),"L56":("FRI","E2"),"L57":("FRI","E3"),"L58":("FRI","E4"),
        "L59":("FRI","E5"),"L60":("FRI","E6"),
    }
    SLOT_BUNDLES = {
        "A1":[("MON",1),("WED",2)],"B1":[("TUE",1),("THU",2)],
        "C1":[("WED",1),("FRI",2)],"D1":[("THU",1),("MON",3)],
        "E1":[("FRI",1),("TUE",3)],"F1":[("MON",2),("WED",3)],
        "G1":[("TUE",2),("THU",3)],
        "A2":[("MON",6),("WED",7)],"B2":[("TUE",6),("THU",7)],
        "C2":[("WED",6),("FRI",7)],"D2":[("THU",6),("MON",8)],
        "E2":[("FRI",6),("TUE",8)],"F2":[("MON",7),("WED",8)],
        "G2":[("TUE",7),("THU",8)],
        "A1+TA1":[("MON",1),("WED",2),("FRI",3)],
        "B1+TB1":[("TUE",1),("THU",2),("MON",4)],
        "C1+TC1":[("WED",1),("FRI",2),("TUE",4)],
        "D1+TD1":[("THU",1),("MON",3),("FRI",5)],
        "E1+TE1":[("FRI",1),("TUE",3),("THU",4)],
        "F1+TF1":[("MON",2),("WED",3),("FRI",4)],
        "G1+TG1":[("TUE",2),("THU",3),("MON",5)],
        "A2+TA2":[("MON",6),("WED",7),("FRI",9)],
        "B2+TB2":[("TUE",6),("THU",7),("MON",9)],
        "C2+TC2":[("WED",6),("FRI",7),("TUE",9)],
        "D2+TD2":[("THU",6),("MON",8),("WED",9)],
        "E2+TE2":[("FRI",6),("TUE",8),("THU",9)],
        "F2+TF2":[("MON",7),("WED",8),("FRI",10)],
        "G2+TG2":[("TUE",7),("THU",8),("MON",10)],
        "A1+TA1+TAA1":[("MON",1),("WED",2),("FRI",3),("TUE",5)],
        "B1+TB1+TBB1":[("TUE",1),("THU",2),("MON",4),("WED",5)],
        "C1+TC1+TCC1":[("WED",1),("FRI",2),("TUE",4),("THU",5)],
        "D1+TD1+TDD1":[("THU",1),("MON",3),("FRI",5),("WED",4)],
        "A2+TA2+TAA2":[("MON",6),("WED",7),("FRI",9),("TUE",10)],
        "B2+TB2+TBB2":[("TUE",6),("THU",7),("MON",9),("WED",10)],
        "C2+TC2+TCC2":[("WED",6),("FRI",7),("TUE",9),("THU",10)],
        "D2+TD2+TDD2":[("THU",6),("MON",8),("WED",9),("FRI",11)],
    }

    def theory_windows(name):
        return [(d,*THEORY_PERIOD_TIMES[p]) for d,p in SLOT_BUNDLES[name]]

    def lab_windows(bundle):
        out = []
        for slot in bundle.split("+"):
            day,pk = LAB_SLOT_MAP[slot]
            s,e = LAB_PERIOD_TIMES[pk]
            out.append((day,s,e))
        return out

    def overlap(w1,w2):
        for d1,s1,e1 in w1:
            for d2,s2,e2 in w2:
                if d1==d2 and max(s1,s2)<min(e1,e2):
                    return True
        return False

    all_theory = list(SLOT_BUNDLES.keys())
    tw = {s:theory_windows(s) for s in all_theory}

    all_lab_bundles = set()
    for v in lab_timetable_data.values():
        all_lab_bundles.add(v["morning"])
        all_lab_bundles.add(v["evening"])
    lw = {b:lab_windows(b) for b in all_lab_bundles}

    TT = {(a,b):overlap(tw[a],tw[b]) for a in all_theory for b in all_theory}
    TL = {(t,l):overlap(tw[t],lw[l]) for t in all_theory for l in all_lab_bundles}
    LL = {(a,b):overlap(lw[a],lw[b]) for a in all_lab_bundles for b in all_lab_bundles}

    SLOT_DAYS = defaultdict(set)
    for slot, periods in SLOT_BUNDLES.items():
        for day,_ in periods:
            SLOT_DAYS[slot].add(day)

    return TT, TL, LL, SLOT_DAYS

TT_OVERLAP, TL_OVERLAP, LL_OVERLAP, SLOT_DAYS = build_overlap_tables(
    json.dumps(data["lab_timetable"], sort_keys=True)
)

def tt_conflict(a,b): return TT_OVERLAP.get((a,b),False)
def tl_conflict(t,l): return TL_OVERLAP.get((t,l),False)
def ll_conflict(a,b): return LL_OVERLAP.get((a,b),False)

# ══════════════════════════════════════════════════════════════════
# COMBO GENERATION
# ══════════════════════════════════════════════════════════════════

def get_all_zero_conflict_combos(sid):
    info     = student_sections[sid]
    sel      = info["selection"]
    courses  = list(sel.keys())
    tcourses = [c for c in courses if sel[c]["type"]=="theory" and c in timetable]
    lcourses = [c for c in courses if sel[c]["type"]=="lab"    and c in lab_timetable]
    nt, nl   = len(tcourses), len(lcourses)
    if nt+nl == 0: return []

    t_opts = [(timetable[c]["morning"], timetable[c]["evening"]) for c in tcourses]
    l_opts = [(lab_timetable[c]["morning"], lab_timetable[c]["evening"]) for c in lcourses]

    valid = []
    for combo in product(*[[0,1]]*(nt+nl)):
        tc = combo[:nt]; lc = combo[nt:]
        ts = [t_opts[i][tc[i]] for i in range(nt)]
        ls = [l_opts[i][lc[i]] for i in range(nl)]
        clash = False
        for i in range(nt):
            for j in range(i+1,nt):
                if tt_conflict(ts[i],ts[j]): clash=True; break
            if clash: break
        if not clash:
            for i in range(nl):
                for j in range(i+1,nl):
                    if ll_conflict(ls[i],ls[j]): clash=True; break
                if clash: break
        if not clash:
            for ti,t in enumerate(ts):
                for li,l in enumerate(ls):
                    if tl_conflict(t,l): clash=True; break
                if clash: break
        if not clash:
            combo_dict = {}
            for i,c in enumerate(tcourses):
                combo_dict[c] = {"type":"theory","section":"morning" if tc[i]==0 else "evening","slot":ts[i]}
            for i,c in enumerate(lcourses):
                combo_dict[c] = {"type":"lab","section":"morning" if lc[i]==0 else "evening","slot":ls[i]}
            valid.append(combo_dict)
    return valid


def score_combo(combo, prefs):
    s = 0
    prefer_time   = prefs.get("prefer_time", "any")
    fixed_courses = prefs.get("fixed_courses", {})
    for course, v in combo.items():
        if prefer_time != "any" and v["section"] == prefer_time:
            s += 3
        if course in fixed_courses and v["section"] == fixed_courses[course]:
            s += 10
        if course in fixed_courses and v["section"] != fixed_courses[course]:
            s -= 20
    return s


def pick_diverse_combos(combos, prefs, n=3):
    if not combos: return []
    prefer_time   = prefs.get("prefer_time", "any")
    fixed_courses = prefs.get("fixed_courses", {})

    def satisfies_fixed(combo):
        for course, sec in fixed_courses.items():
            if course in combo and combo[course]["section"] != sec:
                return False
        return True

    valid = [c for c in combos if satisfies_fixed(c)]
    if not valid:
        valid = combos

    if prefer_time != "any":
        valid = sorted(
            valid,
            key=lambda c: sum(1 for v in c.values() if v["section"] == prefer_time),
            reverse=True
        )
    else:
        valid = sorted(valid, key=lambda c: score_combo(c, prefs), reverse=True)

    picked = []
    for combo in valid:
        if not picked:
            picked.append(combo)
        else:
            diffs = [sum(1 for c in combo if c in p and combo[c]["section"] != p[c]["section"]) for p in picked]
            if all(d >= 2 for d in diffs):
                picked.append(combo)
        if len(picked) == n: break

    if len(picked) < n:
        for combo in valid:
            if combo not in picked:
                picked.append(combo)
            if len(picked) == n: break

    return picked


def find_conflicts(selections):
    courses  = list(selections.keys())
    tcourses = [c for c in courses if selections[c]["type"]=="theory"]
    lcourses = [c for c in courses if selections[c]["type"]=="lab"]
    conflicts = []
    ts = {c: selections[c]["slot"] for c in tcourses}
    ls = {c: selections[c]["slot"] for c in lcourses}
    for i,ca in enumerate(tcourses):
        for cb in tcourses[i+1:]:
            if tt_conflict(ts[ca],ts[cb]):
                conflicts.append((ca,cb,f"{ts[ca]} and {ts[cb]} overlap"))
    for i,ca in enumerate(lcourses):
        for cb in lcourses[i+1:]:
            if ll_conflict(ls[ca],ls[cb]):
                conflicts.append((ca,cb,f"{ls[ca]} and {ls[cb]} overlap"))
    for tc in tcourses:
        for lc in lcourses:
            if tl_conflict(ts[tc],ls[lc]):
                conflicts.append((tc,lc,f"{ts[tc]} and {ls[lc]} overlap"))
    return conflicts

# ══════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family:'Inter',sans-serif; }
.block-container { padding-left:1rem !important; padding-right:1rem !important; }
.tt-table { border-collapse:collapse; width:100%; table-layout:fixed; }
.hdr-label-theory { background:#1E3A5F; color:#E2E8F0; font-weight:700; font-size:11px;
                    text-align:center; padding:6px 4px; border:1px solid #2D4E6F; width:60px; }
.hdr-label-lab    { background:#2C5282; color:#BEE3F8; font-weight:700; font-size:11px;
                    text-align:center; padding:6px 4px; border:1px solid #2D4E6F; width:60px; }
.hdr-theory  { background:#1E3A5F; color:#E2E8F0; font-weight:600; font-size:9px;
               text-align:center; padding:5px 3px; border:1px solid #2D4E6F; line-height:1.4; }
.hdr-lab     { background:#2C5282; color:#BEE3F8; font-weight:600; font-size:9px;
               text-align:center; padding:5px 3px; border:1px solid #2D4E6F; line-height:1.4; }
.hdr-empty-theory { background:#1E3A5F; border:1px solid #2D4E6F; }
.hdr-empty-lab    { background:#2C5282; border:1px solid #2D4E6F; }
.hdr-lunch   { background:#1E3A5F; color:#93C5FD; font-size:13px; font-weight:700;
               text-align:center; border:1px solid #2D4E6F; letter-spacing:3px; }
.day-td      { background:#1E3A5F; color:#93C5FD; font-weight:700; font-size:13px;
               text-align:center; vertical-align:middle; border:1px solid #2D4E6F; width:55px; }
.cell-empty  { background:#F8FAFC; border:1px solid #E2E8F0; padding:4px; vertical-align:top; height:68px; }
.cell-active { background:#EFF6FF; border:1px solid #93C5FD; padding:4px; vertical-align:top; height:68px; }
.cell-lab-active { background:#F0FDF4; border:1px solid #6EE7B7; padding:4px; vertical-align:top; height:68px; }
.cell-blank  { background:#F1F5F9; border:1px solid #E2E8F0; height:68px; }
.cell-student-theory   { background:#D1FAE5; border:2px solid #10B981; padding:4px; vertical-align:top; height:68px; }
.cell-student-lab      { background:#BBF7D0; border:2px solid #059669; padding:4px; vertical-align:top; height:68px; }
.cell-student-conflict { background:#FEE2E2; border:2px solid #EF4444; padding:4px; vertical-align:top; height:68px; }
.conflict-line { font-size:9px; font-weight:700; color:#B91C1C; text-align:center; display:block; line-height:1.4; }
.slot-lbl    { font-size:8px; color:#64748B; font-weight:600; display:block; text-align:center; margin-bottom:2px; }
.course-line { font-size:9px; font-weight:700; color:#1D4ED8; text-align:center; display:block; line-height:1.4; }
.lab-line    { font-size:9px; font-weight:700; color:#15803D; text-align:center; display:block; line-height:1.4; }
.student-course-line { font-size:9px; font-weight:700; color:#065F46; text-align:center; display:block; line-height:1.4; }
.student-lab-line    { font-size:9px; font-weight:700; color:#065F46; text-align:center; display:block; line-height:1.4; }
.clash-badge-red   { background:#FEE2E2; color:#DC2626; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; display:inline-block; }
.clash-badge-green { background:#D1FAE5; color:#065F46; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# GRID
# ══════════════════════════════════════════════════════════════════

DAYS = ["MON","TUE","WED","THU","FRI"]
GRID = {
    "MON":[("A1","L1"),("F1","L2"),("D1","L3"),("TB1","L4"),("TG1","L5"),(None,"L6"),
           ("A2","L31"),("F2","L32"),("D2","L33"),("TB2","L34"),("TG2","L35"),(None,"L36"),("V3",None)],
    "TUE":[("B1","L7"),("G1","L8"),("E1","L9"),("TC1","L10"),("TAA1","L11"),(None,"L12"),
           ("B2","L37"),("G2","L38"),("E2","L39"),("TC2","L40"),("TAA2","L41"),(None,"L42"),("V4",None)],
    "WED":[("C1","L13"),("A1","L14"),("F1","L15"),("V1","L16"),("V2","L17"),(None,"L18"),
           ("C2","L43"),("A2","L44"),("F2","L45"),("TD2","L46"),("TBB2","L47"),(None,"L48"),("V5",None)],
    "THU":[("D1","L19"),("B1","L20"),("G1","L21"),("TE1","L22"),("TCC1","L23"),(None,"L24"),
           ("D2","L49"),("B2","L50"),("G2","L51"),("TE2","L52"),("TCC2","L53"),(None,"L54"),("V6",None)],
    "FRI":[("E1","L25"),("C1","L26"),("TA1","L27"),("TF1","L28"),("TD1","L29"),(None,"L30"),
           ("E2","L55"),("C2","L56"),("TA2","L57"),("TF2","L58"),("TDD2","L59"),(None,"L60"),("V7",None)],
}
THEORY_TIMES = [
    "8:00–8:50 AM","9:00–9:50 AM","10:00–10:50 AM","11:00–11:50 AM","12:00–12:50 PM","",
    "2:00–2:50 PM","3:00–3:50 PM","4:00–4:50 PM","5:00–5:50 PM","6:00–6:50 PM","","7:01–7:50 PM",
]
LAB_TIMES = [
    "8:00–8:50 AM","8:51–9:40 AM","9:51–10:40 AM","10:41–11:30 AM","11:40–12:30 PM","12:31–1:20 PM",
    "2:00–2:50 PM","2:51–3:40 PM","3:51–4:40 PM","4:41–5:30 PM","5:40–6:30 PM","6:31–7:20 PM","",
]

slot_to_courses = defaultdict(list)
for course,slots in timetable.items():
    for bundle in [slots["morning"],slots["evening"]]:
        for part in bundle.split("+"):
            if course not in slot_to_courses[part]:
                slot_to_courses[part].append(course)

lab_slot_to_courses = defaultdict(list)
for lab_code,slots in lab_timetable.items():
    for bundle in [slots["morning"],slots["evening"]]:
        for part in bundle.split("+"):
            if lab_code not in lab_slot_to_courses[part]:
                lab_slot_to_courses[part].append(lab_code)

# ══════════════════════════════════════════════════════════════════
# RENDER HELPERS
# ══════════════════════════════════════════════════════════════════

def render_cell(theory_slot,lab_slot):
    tc = slot_to_courses.get(theory_slot,[]) if theory_slot else []
    lc = lab_slot_to_courses.get(lab_slot,[]) if lab_slot else []
    lbl = f"{theory_slot}/{lab_slot}" if theory_slot and lab_slot else (theory_slot or lab_slot or "")
    content = f'<span class="slot-lbl">{lbl}</span>'
    for c in tc: content += f'<span class="course-line">{c}</span>'
    for c in lc: content += f'<span class="lab-line">{c}</span>'
    cls = "cell-empty" if not tc and not lc else ("cell-lab-active" if lc and not tc else "cell-active")
    return f'<td class="{cls}">{content}</td>'

def get_student_slots(combo):
    theory_slots, lab_slots = set(), set()
    stc = defaultdict(list)
    for course, sel in combo.items():
        for part in sel["slot"].split("+"):
            part = part.strip()
            if sel["type"] == "theory":
                theory_slots.add(part); stc[("theory",part)].append(course)
            else:
                lab_slots.add(part); stc[("lab",part)].append(course)
    return theory_slots, lab_slots, stc

def get_conflicting_courses(combo):
    if not combo: return set()
    courses  = list(combo.keys())
    tcourses = [c for c in courses if combo[c]["type"]=="theory"]
    lcourses = [c for c in courses if combo[c]["type"]=="lab"]
    bad = set()
    ts = {c: combo[c]["slot"] for c in tcourses}
    ls = {c: combo[c]["slot"] for c in lcourses}
    for i,ca in enumerate(tcourses):
        for cb in tcourses[i+1:]:
            if tt_conflict(ts[ca],ts[cb]): bad.add(ca); bad.add(cb)
    for i,ca in enumerate(lcourses):
        for cb in lcourses[i+1:]:
            if ll_conflict(ls[ca],ls[cb]): bad.add(ca); bad.add(cb)
    for tc in tcourses:
        for lc in lcourses:
            if tl_conflict(ts[tc],ls[lc]): bad.add(tc); bad.add(lc)
    return bad

def render_student_cell(tslot,lslot,theory_slots,lab_slots,stc,bad_courses=None):
    bad_courses = bad_courses or set()
    lbl = f"{tslot}/{lslot}" if tslot and lslot else (tslot or lslot or "")
    content = f'<span class="slot-lbl">{lbl}</span>'
    t_hit = tslot and tslot in theory_slots
    l_hit = lslot and lslot in lab_slots
    if t_hit:
        for course in stc.get(("theory",tslot),[]):
            css = "conflict-line" if course in bad_courses else "student-course-line"
            content += f'<span class="{css}">{course}</span>'
    if l_hit:
        for course in stc.get(("lab",lslot),[]):
            css = "conflict-line" if course in bad_courses else "student-lab-line"
            content += f'<span class="{css}">{course}</span>'
    t_bad = t_hit and any(c in bad_courses for c in stc.get(("theory",tslot),[]))
    l_bad = l_hit and any(c in bad_courses for c in stc.get(("lab",lslot),[]))
    cls = ("cell-student-conflict" if t_bad or l_bad
           else "cell-student-theory" if t_hit
           else "cell-student-lab" if l_hit
           else "cell-empty")
    return f'<td class="{cls}">{content}</td>'

def build_timetable_html(combo=None):
    if combo:
        ts,ls,stc = get_student_slots(combo)
        bad = get_conflicting_courses(combo)
    else:
        bad = set()
    html = '<table class="tt-table"><tr>'
    html += '<td class="hdr-label-theory">THEORY<br>HOURS</td>'
    for tt in THEORY_TIMES[:6]:
        html += f'<td class="{"hdr-theory" if tt else "hdr-empty-theory"}">{tt}</td>'
    html += '<td class="hdr-lunch" rowspan="7">L<br>U<br>N<br>C<br>H</td>'
    for tt in THEORY_TIMES[6:]:
        html += f'<td class="{"hdr-theory" if tt else "hdr-empty-theory"}">{tt}</td>'
    html += '</tr><tr><td class="hdr-label-lab">LAB<br>HOURS</td>'
    for lt in LAB_TIMES[:6]:
        html += f'<td class="{"hdr-lab" if lt else "hdr-empty-lab"}">{lt}</td>'
    for lt in LAB_TIMES[6:]:
        html += f'<td class="{"hdr-lab" if lt else "hdr-empty-lab"}">{lt}</td>'
    html += "</tr>"
    for day in DAYS:
        html += f"<tr><td class='day-td'>{day}</td>"
        for tslot,lslot in GRID[day][:6]:
            if tslot is None and lslot is None: html += '<td class="cell-blank"></td>'
            elif combo: html += render_student_cell(tslot,lslot,ts,ls,stc,bad)
            else: html += render_cell(tslot,lslot)
        for tslot,lslot in GRID[day][6:]:
            if tslot is None and lslot is None: html += '<td class="cell-blank"></td>'
            elif combo: html += render_student_cell(tslot,lslot,ts,ls,stc,bad)
            else: html += render_cell(tslot,lslot)
        html += "</tr>"
    html += "</table>"
    return html

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

st.title("📅 VIT  — FFCS Timetable Generator")

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Theory Courses",   metrics["total_theory_courses"])
c2.metric("Lab Courses",      metrics["total_lab_courses"])
c3.metric("Total Students",   metrics["total_students"])
c4.metric("✅ Fully Solvable", metrics["solvable_students"])
c5.metric("⚠️ Unsolvable",    metrics["full_unsolvable"])
c6.metric("Solvable %",       f"{metrics['solvable_pct']}%")

st.divider()

tab1, tab2 = st.tabs([
    "🏫 Institutional Timetable",
    "👤 Student Timetable Options",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════

with tab1:
    st.markdown(build_timetable_html(), unsafe_allow_html=True)
    st.divider()
    col_t, col_l = st.columns(2)
    with col_t:
        st.markdown("### 🎓 Theory")
        rows = [
            {
                "Code":       c,
                "Name":       course_name_map.get(c,"")[:40],
                "Enrolments": theory_demand[c],
                "🌅 Morning": s["morning"],
                "🌆 Evening": s["evening"],
            }
            for c, s in sorted(timetable.items(), key=lambda x: -theory_demand[x[0]])
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    with col_l:
        st.markdown("### 🔬 Lab")
        rows = [
            {
                "Code":       c,
                "Name":       course_name_map.get(c,"")[:35],
                "Enrolments": lab_demand[c],
                "🌅 Morning": s["morning"],
                "🌆 Evening": s["evening"],
            }
            for c, s in sorted(lab_timetable.items(), key=lambda x: -lab_demand[x[0]])
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════════════════════════

with tab2:
    st.markdown("### 👤 Student Timetable Options")

    all_sids = sorted(student_sections.keys())
    sel_sid  = st.selectbox(
        "Select Student", all_sids,
        format_func=lambda s: f"{s} — {student_sections[s]['name']}"
    )

    if st.session_state.get("last_sid") != sel_sid:
        for key in list(st.session_state.keys()):
            if key.startswith(f"applied_prefs_") or key.startswith(f"fc_") or key.startswith(f"pt_") or key.startswith(f"carousel_radio_"):
                del st.session_state[key]
        st.session_state["last_sid"] = sel_sid

    if sel_sid:
        info     = student_sections[sel_sid]
        courses  = list(info["selection"].keys())
        tcourses = [c for c in courses if info["selection"][c]["type"]=="theory" and c in timetable]
        lcourses = [c for c in courses if info["selection"][c]["type"]=="lab"    and c in lab_timetable]

        btn1, btn2 = st.columns(2)

        @st.dialog(f"Timetable Options — {info['name']}", width="large")
        def show_carousel():
            all_combos = get_all_zero_conflict_combos(sel_sid)
            if not all_combos:
                st.warning("No conflict-free combination exists. Showing least-conflict option.")
                fallback = student_sections[sel_sid]["selection"]
                if not fallback:
                    st.error("No schedule data available for this student.")
                    return
                st.markdown("🟩 Theory &nbsp;|&nbsp; 🟢 Lab &nbsp;|&nbsp; 🟥 Conflict")
                st.markdown(build_timetable_html(combo=fallback), unsafe_allow_html=True)
                rows = []
                for course, sel in sorted(fallback.items()):
                    rows.append({
                        "Course":  course,
                        "Name":    course_name_map.get(course,"")[:35],
                        "Type":    "🎓 Theory" if sel["type"]=="theory" else "🔬 Lab",
                        "Section": "🌅 Morning" if sel["section"]=="morning" else "🌆 Evening",
                        "Slot":    sel["slot"],
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                            height=min(35*len(rows)+38, 280))
                return

            pref_key = f"applied_prefs_{sel_sid}"
            if pref_key not in st.session_state:
                st.session_state[pref_key] = {"prefer_time": "any", "fixed_courses": {}}

            with st.expander("🎛 Set My Preferences", expanded=False):
                prefer_time = st.radio(
                    "Preferred time",
                    ["No preference", "Morning", "Evening"],
                    horizontal=True,
                    key=f"pt_{sel_sid}"
                )

                st.markdown("**Fix specific courses:**")
                fixed_courses = {}
                all_pref_courses = sorted(tcourses + lcourses)
                for i in range(0, len(all_pref_courses), 3):
                    row_courses = all_pref_courses[i:i+3]
                    cols = st.columns(3)
                    for col, course in zip(cols, row_courses):
                        with col:
                            ctype = "🎓" if course in tcourses else "🔬"
                            ch = st.selectbox(
                                f"{ctype} {course}",
                                ["Any", "Morning", "Evening"],
                                key=f"fc_{sel_sid}_{course}"
                            )
                            if ch != "Any":
                                fixed_courses[course] = ch.lower()

                if st.button("✅ Apply Preferences", key=f"apply_prefs_{sel_sid}",
                             type="primary", use_container_width=True):
                    st.session_state[pref_key] = {
                        "prefer_time":   prefer_time.lower() if prefer_time != "No preference" else "any",
                        "fixed_courses": fixed_courses,
                    }
                    st.success("Preferences applied.")

                if st.button("🔄 Reset Preferences", key=f"reset_prefs_{sel_sid}", use_container_width=True):
                    for key in list(st.session_state.keys()):
                        if key.startswith(f"fc_{sel_sid}_") or key == f"pt_{sel_sid}" or key == f"applied_prefs_{sel_sid}":
                            if st.session_state.get(key) is not None:
                                del st.session_state[key]
                    st.success("Preferences reset.")
                    st.rerun()

            ap = st.session_state[pref_key]
            pill_parts = []
            if ap["prefer_time"] != "any":
                pill_parts.append(f"🕐 {ap['prefer_time'].capitalize()}")
            for course, sec in ap["fixed_courses"].items():
                pill_parts.append(f"📌 {course} → {sec}")
            if pill_parts:
                st.markdown(" &nbsp;|&nbsp; ".join(
                    f"<span style='background:#EFF6FF;border:1px solid #93C5FD;border-radius:4px;"
                    f"padding:2px 8px;font-size:12px;color:#1D4ED8;font-weight:600'>{p}</span>"
                    for p in pill_parts), unsafe_allow_html=True)
            else:
                st.caption("No preferences applied.")

            prefs = st.session_state[pref_key]
            prefs_applied = prefs["prefer_time"] != "any" or bool(prefs["fixed_courses"])
            diverse = pick_diverse_combos(all_combos, prefs, n=3)
            total   = len(diverse)
            st.markdown(f"**{len(all_combos)}** zero-conflict option(s). Showing **{total}** diverse.")

            option_labels  = [f"Option {i+1}" for i in range(total)]
            selected_label = st.radio("", option_labels, horizontal=True,
                                      label_visibility="collapsed", key=f"carousel_radio_{sel_sid}")
            idx = option_labels.index(selected_label)

            st.markdown(f"<div style='text-align:center;font-weight:700;font-size:15px;padding:8px;"
                        f"background:#EFF6FF;border-radius:6px;margin-bottom:8px'>Option {idx+1}</div>",
                        unsafe_allow_html=True)

            if prefs_applied:
                lines = []
                combo = diverse[idx]

                if prefs["prefer_time"] != "any":
                    preferred     = prefs["prefer_time"]
                    satisfied     = [c for c,v in combo.items() if v["section"] == preferred]
                    not_satisfied = [c for c,v in combo.items() if v["section"] != preferred]
                    total_c       = len(combo)
                    if not not_satisfied:
                        lines.append(f"✅ All {total_c} courses in **{preferred}** sections.")
                    elif not satisfied:
                        lines.append(f"❌ Could not assign any course to **{preferred}** — no conflict-free option available.")
                    else:
                        lines.append(
                            f"🟡 **{preferred.capitalize()}** preference: {len(satisfied)}/{total_c} courses satisfied. "
                            f"{', '.join(satisfied)} in {preferred}; "
                            f"{', '.join(not_satisfied)} could not be moved without conflict."
                        )

                for course, wanted_sec in prefs["fixed_courses"].items():
                    actual = combo.get(course, {}).get("section")
                    if actual == wanted_sec:
                        lines.append(f"✅ **{course}** fixed to **{wanted_sec}**.")
                    elif actual:
                        lines.append(f"❌ **{course}** could not be fixed to {wanted_sec} without conflict — assigned {actual} instead.")
                    else:
                        lines.append(f"⚠️ **{course}** not found in this timetable option.")

                if lines:
                    st.markdown("\n\n".join(lines))

            st.markdown("🟩 Theory &nbsp;|&nbsp; 🟢 Lab")
            st.markdown(build_timetable_html(combo=diverse[idx]), unsafe_allow_html=True)

            rows = []
            for course, sel in sorted(diverse[idx].items()):
                rows.append({
                    "Course":  course,
                    "Name":    course_name_map.get(course,"")[:35],
                    "Type":    "🎓 Theory" if sel["type"]=="theory" else "🔬 Lab",
                    "Section": "🌅 Morning" if sel["section"]=="morning" else "🌆 Evening",
                    "Slot":    sel["slot"],
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                         height=min(35*len(rows)+38, 280))

        @st.dialog(f"Build My Timetable — {info['name']}", width="large")
        def show_builder():
            st.markdown("**Toggle sections:**")
            for course in sorted(tcourses):
                m_slot = timetable[course]["morning"]
                e_slot = timetable[course]["evening"]
                col_c, col_t = st.columns([2,3])
                with col_c:
                    st.markdown(f"**{course}** 🎓")
                    st.caption(course_name_map.get(course,"")[:30])
                with col_t:
                    st.radio("", [f"🌅 Morning ({m_slot})", f"🌆 Evening ({e_slot})"],
                             horizontal=True, key=f"build_{sel_sid}_{course}", label_visibility="collapsed")

            for course in sorted(lcourses):
                m_slot = lab_timetable[course]["morning"]
                e_slot = lab_timetable[course]["evening"]
                col_c, col_t = st.columns([2,3])
                with col_c:
                    st.markdown(f"**{course}** 🔬")
                    st.caption(course_name_map.get(course,"")[:30])
                with col_t:
                    st.radio("", [f"🌅 Morning ({m_slot})", f"🌆 Evening ({e_slot})"],
                             horizontal=True, key=f"build_{sel_sid}_{course}", label_visibility="collapsed")

            selections = {}
            for course in sorted(tcourses):
                m_slot  = timetable[course]["morning"]
                e_slot  = timetable[course]["evening"]
                choice  = st.session_state.get(f"build_{sel_sid}_{course}", f"🌅 Morning ({m_slot})")
                section = "morning" if "Morning" in choice else "evening"
                selections[course] = {"type":"theory","section":section,"slot":m_slot if section=="morning" else e_slot}
            for course in sorted(lcourses):
                m_slot  = lab_timetable[course]["morning"]
                e_slot  = lab_timetable[course]["evening"]
                choice  = st.session_state.get(f"build_{sel_sid}_{course}", f"🌅 Morning ({m_slot})")
                section = "morning" if "Morning" in choice else "evening"
                selections[course] = {"type":"lab","section":section,"slot":m_slot if section=="morning" else e_slot}

            st.divider()
            conflicts = find_conflicts(selections)
            if conflicts:
                st.error(f"⚠️ {len(conflicts)} conflict(s):")
                for c1, c2, reason in conflicts:
                    st.markdown(f"- **{c1}** ({selections[c1]['slot']}) ↔ **{c2}** ({selections[c2]['slot']}) — {reason}")
            else:
                st.success("✅ No conflicts — valid timetable!")
            st.markdown("🟩 Theory &nbsp;|&nbsp; 🟢 Lab &nbsp;|&nbsp; 🟥 Conflict")
            st.markdown(build_timetable_html(combo=selections), unsafe_allow_html=True)

        with btn1:
            if st.button("See your FFCS planner", use_container_width=True, key=f"carousel_{sel_sid}"):
                show_carousel()
        with btn2:
            if st.button("🛠 Build your Own Timetable", use_container_width=True, key=f"builder_{sel_sid}"):
                show_builder()