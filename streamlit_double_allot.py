"""
FFCS VIT Chennai — Two-Section Timetable Dashboard (Theory + Lab)
=================================================================
Shows:
  1. Institutional timetable (morning + evening slots, theory + lab)
  2. Per-student optimal section recommendation (top 10 conflicted)
  3. Full timetable grid like the VIT FFCS image
  4. Lab course summary tab
"""

import json
import streamlit as st
import pandas as pd
from collections import defaultdict

st.set_page_config(page_title="VIT Chennai FFCS — Two-Section Timetable", layout="wide")

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

timetable        = data["timetable"]        # {course: {morning, evening}}
lab_timetable    = data["lab_timetable"]    # {lab_code: {morning, evening}}
metrics          = data["metrics"]
student_sections = data["student_sections"] # {sid: {name, clashes, selection}}

# ══════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }
.block-container { padding-left: 1rem !important; padding-right: 1rem !important; }

/* ── Timetable grid ────────────────────────────────────────────── */
.tt-table { border-collapse: collapse; width: 100%; table-layout: fixed; }
.hdr-label-theory { background:#1E3A5F; color:#E2E8F0; font-weight:700; font-size:11px;
                    text-align:center; padding:6px 4px; border:1px solid #2D4E6F; width:60px; }
.hdr-label-lab    { background:#2C5282; color:#BEE3F8; font-weight:700; font-size:11px;
                    text-align:center; padding:6px 4px; border:1px solid #2D4E6F; width:60px; }
.hdr-theory       { background:#1E3A5F; color:#E2E8F0; font-weight:600; font-size:9px;
                    text-align:center; padding:5px 3px; border:1px solid #2D4E6F; line-height:1.4; }
.hdr-lab          { background:#2C5282; color:#BEE3F8; font-weight:600; font-size:9px;
                    text-align:center; padding:5px 3px; border:1px solid #2D4E6F; line-height:1.4; }
.hdr-empty-theory { background:#1E3A5F; border:1px solid #2D4E6F; }
.hdr-empty-lab    { background:#2C5282; border:1px solid #2D4E6F; }
.hdr-lunch        { background:#1E3A5F; color:#93C5FD; font-size:13px; font-weight:700;
                    text-align:center; border:1px solid #2D4E6F; letter-spacing:3px; }
.day-td           { background:#1E3A5F; color:#93C5FD; font-weight:700; font-size:13px;
                    text-align:center; vertical-align:middle; border:1px solid #2D4E6F; width:55px; }
.cell-empty       { background:#F8FAFC; border:1px solid #E2E8F0; padding:4px;
                    vertical-align:top; height:68px; }
.cell-active      { background:#EFF6FF; border:1px solid #93C5FD; padding:4px;
                    vertical-align:top; height:68px; }
.cell-lab-active  { background:#F0FDF4; border:1px solid #6EE7B7; padding:4px;
                    vertical-align:top; height:68px; }
.cell-blank       { background:#F1F5F9; border:1px solid #E2E8F0; height:68px; }
.slot-lbl         { font-size:8px; color:#64748B; font-weight:600; display:block;
                    text-align:center; margin-bottom:2px; }
.course-line      { font-size:9px; font-weight:700; color:#1D4ED8; text-align:center;
                    display:block; line-height:1.4; }
.lab-line         { font-size:9px; font-weight:700; color:#15803D; text-align:center;
                    display:block; line-height:1.4; }

/* ── Student cards ──────────────────────────────────────────────── */
.student-card { background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;
                padding:12px; margin-bottom:12px; }
.student-name { font-size:15px; font-weight:700; color:#1E3A5F; margin-bottom:4px; }
.clash-badge-red   { background:#FEE2E2; color:#DC2626; border-radius:4px;
                     padding:2px 8px; font-size:11px; font-weight:600; display:inline-block; }
.clash-badge-green { background:#D1FAE5; color:#065F46; border-radius:4px;
                     padding:2px 8px; font-size:11px; font-weight:600; display:inline-block; }

/* ── Legend pills ───────────────────────────────────────────────── */
.legend-theory { display:inline-block; background:#EFF6FF; border:1px solid #93C5FD;
                 color:#1D4ED8; border-radius:4px; padding:2px 8px; font-size:11px;
                 font-weight:600; margin-right:6px; }
.legend-lab    { display:inline-block; background:#F0FDF4; border:1px solid #6EE7B7;
                 color:#15803D; border-radius:4px; padding:2px 8px; font-size:11px;
                 font-weight:600; margin-right:6px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# BUILD SLOT → COURSES MAPS
# ══════════════════════════════════════════════════════════════════

# Theory slots → courses
slot_to_courses = defaultdict(list)
for course, slots in timetable.items():
    for bundle in [slots["morning"], slots["evening"]]:
        for part in bundle.split("+"):
            if course not in slot_to_courses[part]:
                slot_to_courses[part].append(course)

# Lab slots → lab courses
lab_slot_to_courses = defaultdict(list)
for lab_code, slots in lab_timetable.items():
    for bundle in [slots["morning"], slots["evening"]]:
        for part in bundle.split("+"):
            if lab_code not in lab_slot_to_courses[part]:
                lab_slot_to_courses[part].append(lab_code)

# ══════════════════════════════════════════════════════════════════
# TIMETABLE GRID DEFINITION  (exact VIT FFCS layout)
# ══════════════════════════════════════════════════════════════════

DAYS = ["MON", "TUE", "WED", "THU", "FRI"]

GRID = {
    "MON": [
        ("A1","L1"),("F1","L2"),("D1","L3"),("TB1","L4"),("TG1","L5"),(None,"L6"),
        ("A2","L31"),("F2","L32"),("D2","L33"),("TB2","L34"),("TG2","L35"),(None,"L36"),("V3",None),
    ],
    "TUE": [
        ("B1","L7"),("G1","L8"),("E1","L9"),("TC1","L10"),("TAA1","L11"),(None,"L12"),
        ("B2","L37"),("G2","L38"),("E2","L39"),("TC2","L40"),("TAA2","L41"),(None,"L42"),("V4",None),
    ],
    "WED": [
        ("C1","L13"),("A1","L14"),("F1","L15"),("V1","L16"),("V2",None),(None,None),
        ("C2","L43"),("A2","L44"),("F2","L45"),("TD2","L46"),("TBB2","L47"),(None,"L48"),("V5",None),
    ],
    "THU": [
        ("D1","L19"),("B1","L20"),("G1","L21"),("TE1","L22"),("TCC1","L23"),(None,"L24"),
        ("D2","L49"),("B2","L50"),("G2","L51"),("TE2","L52"),("TCC2","L53"),(None,"L54"),("V6",None),
    ],
    "FRI": [
        ("E1","L25"),("C1","L26"),("TA1","L27"),("TF1","L28"),("TD1","L29"),(None,"L30"),
        ("E2","L55"),("C2","L56"),("TA2","L57"),("TF2","L58"),("TDD2","L59"),(None,"L60"),("V7",None),
    ],
}

THEORY_TIMES = [
    "8:00–8:50 AM","9:00–9:50 AM","10:00–10:50 AM","11:00–11:50 AM","12:00–12:50 PM","",
    "2:00–2:50 PM","3:00–3:50 PM","4:00–4:50 PM","5:00–5:50 PM","6:00–6:50 PM","","7:01–7:50 PM",
]
LAB_TIMES = [
    "8:00–8:50 AM","8:51–9:40 AM","9:51–10:40 AM","10:41–11:30 AM","11:40–12:30 PM","12:31–1:20 PM",
    "2:00–2:50 PM","2:51–3:40 PM","3:51–4:40 PM","4:41–5:30 PM","5:40–6:30 PM","6:31–7:20 PM","",
]

# ══════════════════════════════════════════════════════════════════
# RENDER TIMETABLE CELL
# ══════════════════════════════════════════════════════════════════

def render_cell(theory_slot, lab_slot):
    t_courses = slot_to_courses.get(theory_slot, []) if theory_slot else []
    l_courses = lab_slot_to_courses.get(lab_slot, []) if lab_slot else []
    has_theory = bool(t_courses)
    has_lab    = bool(l_courses)

    if theory_slot and lab_slot:
        lbl = f"{theory_slot}/{lab_slot}"
    elif theory_slot:
        lbl = theory_slot
    elif lab_slot:
        lbl = lab_slot
    else:
        lbl = ""

    content = f'<span class="slot-lbl">{lbl}</span>'
    for c in t_courses:
        content += f'<span class="course-line">{c}</span>'
    for c in l_courses:
        content += f'<span class="lab-line">{c}</span>'

    if has_theory and has_lab:
        td_class = "cell-active"      # both — blue border (theory wins display)
    elif has_lab:
        td_class = "cell-lab-active"  # lab-only — green border
    elif has_theory:
        td_class = "cell-active"      # theory-only — blue border
    else:
        td_class = "cell-empty"

    return f'<td class="{td_class}">{content}</td>'


def build_timetable_html():
    html = '<table class="tt-table">'

    # Row 1: Theory header
    html += "<tr>"
    html += '<td class="hdr-label-theory">THEORY<br>HOURS</td>'
    for tt in THEORY_TIMES[:6]:
        cls = "hdr-theory" if tt else "hdr-empty-theory"
        html += f'<td class="{cls}">{tt}</td>'
    html += '<td class="hdr-lunch" rowspan="7">L<br>U<br>N<br>C<br>H</td>'
    for tt in THEORY_TIMES[6:]:
        cls = "hdr-theory" if tt else "hdr-empty-theory"
        html += f'<td class="{cls}">{tt}</td>'
    html += "</tr>"

    # Row 2: Lab header
    html += "<tr>"
    html += '<td class="hdr-label-lab">LAB<br>HOURS</td>'
    for lt in LAB_TIMES[:6]:
        cls = "hdr-lab" if lt else "hdr-empty-lab"
        html += f'<td class="{cls}">{lt}</td>'
    for lt in LAB_TIMES[6:]:
        cls = "hdr-lab" if lt else "hdr-empty-lab"
        html += f'<td class="{cls}">{lt}</td>'
    html += "</tr>"

    # Data rows
    for day in DAYS:
        html += "<tr>"
        html += f'<td class="day-td">{day}</td>'
        for theory_slot, lab_slot in GRID[day][:6]:
            if theory_slot is None and lab_slot is None:
                html += '<td class="cell-blank"></td>'
            else:
                html += render_cell(theory_slot, lab_slot)
        for theory_slot, lab_slot in GRID[day][6:]:
            if theory_slot is None and lab_slot is None:
                html += '<td class="cell-blank"></td>'
            else:
                html += render_cell(theory_slot, lab_slot)
        html += "</tr>"

    html += "</table>"
    return html

# ══════════════════════════════════════════════════════════════════
# HELPER: type badge HTML
# ══════════════════════════════════════════════════════════════════

def type_badge(t):
    if t == "theory":
        return '<span class="legend-theory">Theory</span>'
    return '<span class="legend-lab">Lab</span>'


# ══════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════

st.title("📅 VIT Chennai — FFCS Two-Section Timetable (Theory + Lab)")

# Metrics row
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Theory Courses", metrics["total_theory_courses"])
c2.metric("Lab Courses",    metrics["total_lab_courses"])
c3.metric("Total Students", metrics["total_students"])
c4.metric("✅ Fully Solvable", metrics["solvable_students"])
c5.metric("⚠️ Unsolvable",   metrics["full_unsolvable"])
c6.metric("Solvable %",     f"{metrics['solvable_pct']}%")

st.divider()

# ── Tab layout ────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏫 Institutional Timetable",
    "👤 Student Section Recommendations",
    "📊 Theory Course Summary",
    "🔬 Lab Course Summary",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1: INSTITUTIONAL TIMETABLE
# ══════════════════════════════════════════════════════════════════

with tab1:
    st.markdown(
        '<span class="legend-theory">Blue cell</span> = Theory course assigned &nbsp;|&nbsp; '
        '<span class="legend-lab">Green cell</span> = Lab course assigned',
        unsafe_allow_html=True,
    )
    st.markdown(build_timetable_html(), unsafe_allow_html=True)
    st.caption("Theory slot labels shown as slot/lab-pair (e.g. A1/L1). Lab slots shown as pairs (L1+L2 etc.).")

    st.divider()

    col_t, col_l = st.columns(2)

    with col_t:
        st.markdown("### 🎓 Theory Course Slot Table")
        rows = []
        for course, slots in sorted(timetable.items()):
            rows.append({
                "Course Code": course,
                "Course Name": course_name_map.get(course, "")[:40],
                "🌅 Morning Slot": slots["morning"],
                "🌆 Evening Slot": slots["evening"],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with col_l:
        st.markdown("### 🔬 Lab Course Slot Table")
        lab_rows = []
        for lab_code, slots in sorted(lab_timetable.items()):
            lab_rows.append({
                "Lab Code":      lab_code,
                "Course Name":   course_name_map.get(lab_code, "")[:35],
                "🌅 Morning Lab": slots["morning"],
                "🌆 Evening Lab": slots["evening"],
            })
        st.dataframe(pd.DataFrame(lab_rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# TAB 2: PER-STUDENT SECTION RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════════

with tab2:
    st.markdown("### Optimal Section Assignment — Top 10 Most Conflicted Students")
    st.markdown(
        "For each student, the best combination of morning/evening sections "
        "is shown (theory **and** lab courses). "
        "🟢 = zero-conflict timetable achieved. 🔴 = unavoidable conflicts remain."
    )

    # Sort by clashes descending, take top 10
    top10 = sorted(student_sections.items(),
                   key=lambda x: x[1]["clashes"], reverse=True)[:10]

    for sid, info in top10:
        solvable = info["solvable"]
        badge_html = (
            '<span class="clash-badge-green">✅ Zero Conflicts</span>'
            if solvable else
            f'<span class="clash-badge-red">⚠️ {info["clashes"]} Conflict(s) Unavoidable</span>'
        )

        st.markdown(f"""
        <div class="student-card">
          <div class="student-name">{info["name"]} &nbsp;
            <span style="color:#64748B;font-size:12px">{sid}</span>
          </div>
          {badge_html}
        </div>
        """, unsafe_allow_html=True)

        if info["selection"]:
            rows = []
            for course, sel in sorted(info["selection"].items()):
                rows.append({
                    "Course": course,
                    "Name":   course_name_map.get(course, "")[:35],
                    "Type":   "🎓 Theory" if sel["type"] == "theory" else "🔬 Lab",
                    "Section": "🌅 Morning" if sel["section"] == "morning" else "🌆 Evening",
                    "Slot":   sel["slot"],
                })
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
                height=min(35 * len(rows) + 38, 350),
            )
        st.markdown("---")

    st.divider()
    st.markdown("### All Students — Conflict Summary")

    all_rows = []
    for sid, info in sorted(student_sections.items(),
                             key=lambda x: x[1]["clashes"], reverse=True):
        sel = info["selection"]
        n_theory = sum(1 for v in sel.values() if v["type"] == "theory")
        n_lab    = sum(1 for v in sel.values() if v["type"] == "lab")
        all_rows.append({
            "Student ID":          sid,
            "Name":                info["name"],
            "Status":              "✅ Solvable" if info["solvable"] else "⚠️ Unsolvable",
            "Remaining Conflicts": info["clashes"],
            "Theory Courses":      n_theory,
            "Lab Courses":         n_lab,
            "Total Courses":       n_theory + n_lab,
        })
    st.dataframe(pd.DataFrame(all_rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# TAB 3: THEORY COURSE SUMMARY
# ══════════════════════════════════════════════════════════════════

with tab3:
    st.markdown("### Theory Course Demand & Slot Assignment")

    # Count students per theory course
    theory_demand = defaultdict(int)
    for s in recs:
        for c in s["recommended_courses"]:
            if c in timetable:
                theory_demand[c] += 1

    # How many unsolvable students take each theory course
    theory_unsolvable = defaultdict(int)
    for sid, info in student_sections.items():
        if not info["solvable"]:
            for c, sel in info["selection"].items():
                if sel["type"] == "theory":
                    theory_unsolvable[c] += 1

    # Morning/evening section counts from student selections
    theory_morning_cnt = defaultdict(int)
    theory_evening_cnt = defaultdict(int)
    for info in student_sections.values():
        for c, sel in info["selection"].items():
            if sel["type"] == "theory":
                if sel["section"] == "morning":
                    theory_morning_cnt[c] += 1
                else:
                    theory_evening_cnt[c] += 1

    rows = []
    for course, slots in sorted(timetable.items(), key=lambda x: -theory_demand[x[0]]):
        total = theory_morning_cnt[course] + theory_evening_cnt[course]
        rows.append({
            "Course":          course,
            "Name":            course_name_map.get(course, "")[:35],
            "Enrolments":      theory_demand[course],
            "🌅 Morning Slot": slots["morning"],
            "🌆 Evening Slot": slots["evening"],
            "🌅 Assigned":     theory_morning_cnt[course],
            "🌆 Assigned":     theory_evening_cnt[course],
            "In Unsolvable":   theory_unsolvable.get(course, 0),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Theory Slot Usage")
    morning_counts = defaultdict(int)
    evening_counts = defaultdict(int)
    for course, slots in timetable.items():
        morning_counts[slots["morning"]] += 1
        evening_counts[slots["evening"]] += 1

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🌅 Morning Slot Usage**")
        m_rows = sorted(morning_counts.items(), key=lambda x: -x[1])
        st.dataframe(pd.DataFrame(m_rows, columns=["Slot", "# Courses"]),
                     use_container_width=True, hide_index=True)
    with col2:
        st.markdown("**🌆 Evening Slot Usage**")
        e_rows = sorted(evening_counts.items(), key=lambda x: -x[1])
        st.dataframe(pd.DataFrame(e_rows, columns=["Slot", "# Courses"]),
                     use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# TAB 4: LAB COURSE SUMMARY
# ══════════════════════════════════════════════════════════════════

with tab4:
    st.markdown("### 🔬 Lab Course Demand & Slot Assignment")

    # Count students per lab course
    lab_demand = defaultdict(int)
    for s in recs:
        for c in s["recommended_courses"]:
            if c in lab_timetable:
                lab_demand[c] += 1

    # Unsolvable students per lab course
    lab_unsolvable = defaultdict(int)
    for sid, info in student_sections.items():
        if not info["solvable"]:
            for c, sel in info["selection"].items():
                if sel["type"] == "lab":
                    lab_unsolvable[c] += 1

    # Morning/evening section preference counts
    lab_morning_cnt = defaultdict(int)
    lab_evening_cnt = defaultdict(int)
    for info in student_sections.values():
        for c, sel in info["selection"].items():
            if sel["type"] == "lab":
                if sel["section"] == "morning":
                    lab_morning_cnt[c] += 1
                else:
                    lab_evening_cnt[c] += 1

    lab_rows = []
    for lab_code, slots in sorted(lab_timetable.items(), key=lambda x: -lab_demand[x[0]]):
        lab_rows.append({
            "Lab Code":        lab_code,
            "Name":            course_name_map.get(lab_code, "")[:35],
            "Enrolments":      lab_demand[lab_code],
            "🌅 Morning Slots": slots["morning"],
            "🌆 Evening Slots": slots["evening"],
            "🌅 Assigned":      lab_morning_cnt[lab_code],
            "🌆 Assigned":      lab_evening_cnt[lab_code],
            "In Unsolvable":   lab_unsolvable.get(lab_code, 0),
        })
    st.dataframe(pd.DataFrame(lab_rows), use_container_width=True, hide_index=True)

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🌅 Morning Lab Slot Usage")
        m_lab_cnt = defaultdict(int)
        for slots in lab_timetable.values():
            m_lab_cnt[slots["morning"]] += 1
        m_lab_rows = sorted(m_lab_cnt.items(), key=lambda x: -x[1])
        st.dataframe(pd.DataFrame(m_lab_rows, columns=["Lab Bundle", "# Courses"]),
                     use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("### 🌆 Evening Lab Slot Usage")
        e_lab_cnt = defaultdict(int)
        for slots in lab_timetable.values():
            e_lab_cnt[slots["evening"]] += 1
        e_lab_rows = sorted(e_lab_cnt.items(), key=lambda x: -x[1])
        st.dataframe(pd.DataFrame(e_lab_rows, columns=["Lab Bundle", "# Courses"]),
                     use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Lab ↔ Theory Pairing")
    st.markdown("Each lab course and the theory course it is paired with (if any).")

    pair_rows = []
    for lab_code, slots in sorted(lab_timetable.items()):
        # Infer theory pair: same prefix without trailing 'P'
        theory_code = lab_code.replace("P", "L") if lab_code.endswith("P") else None
        theory_slot_m = timetable.get(theory_code, {}).get("morning", "—") if theory_code else "—"
        theory_slot_e = timetable.get(theory_code, {}).get("evening", "—") if theory_code else "—"
        pair_rows.append({
            "Lab Code":         lab_code,
            "Theory Code":      theory_code if theory_code in timetable else "—",
            "Lab 🌅 Morning":   slots["morning"],
            "Lab 🌆 Evening":   slots["evening"],
            "Theory 🌅 Morning": theory_slot_m,
            "Theory 🌆 Evening": theory_slot_e,
        })
    st.dataframe(pd.DataFrame(pair_rows), use_container_width=True, hide_index=True)