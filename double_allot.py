# # """
# # FFCS VIT Chennai — Two-Section SA (Theory Only)
# # ================================================
# # Each theory course gets TWO slots:
# #   - morning_slot: one bundle from MORNING_BUNDLES
# #   - evening_slot: one bundle from EVENING_BUNDLES

# # Objective: minimize students for whom NO conflict-free
# # section combination exists across all their theory courses.

# # A student is "unsolvable" if for every 2^n combination of
# # morning/evening sections across their n courses, at least
# # one pair of slots overlaps.

# # Phase 2: per-student optimal section assignment by enumeration.
# # """

# # import json, math, random, time
# # from collections import defaultdict, Counter
# # from itertools import combinations, product

# # random.seed(42)

# # # ══════════════════════════════════════════════════════════════════
# # # SLOT DATA
# # # ══════════════════════════════════════════════════════════════════

# # THEORY_PERIOD_TIMES = {
# #     1:(480,530),  2:(535,585),  3:(590,640),  4:(705,750),
# #     5:(755,805),  6:(840,890),  7:(895,945),  8:(950,1000),
# #     9:(1005,1055),10:(1060,1110),11:(1115,1165)
# # }

# # SLOT_BUNDLES = {
# #     "A1":[("MON",1),("WED",2)],  "B1":[("TUE",1),("THU",2)],
# #     "C1":[("WED",1),("FRI",2)],  "D1":[("THU",1),("MON",3)],
# #     "E1":[("FRI",1),("TUE",3)],  "F1":[("MON",2),("WED",3)],
# #     "G1":[("TUE",2),("THU",3)],
# #     "A2":[("MON",6),("WED",7)],  "B2":[("TUE",6),("THU",7)],
# #     "C2":[("WED",6),("FRI",7)],  "D2":[("THU",6),("MON",8)],
# #     "E2":[("FRI",6),("TUE",8)],  "F2":[("MON",7),("WED",8)],
# #     "G2":[("TUE",7),("THU",8)],
# #     "A1+TA1":[("MON",1),("WED",2),("FRI",3)],
# #     "B1+TB1":[("TUE",1),("THU",2),("MON",4)],
# #     "C1+TC1":[("WED",1),("FRI",2),("TUE",4)],
# #     "D1+TD1":[("THU",1),("MON",3),("FRI",5)],
# #     "E1+TE1":[("FRI",1),("TUE",3),("THU",4)],
# #     "F1+TF1":[("MON",2),("WED",3),("FRI",4)],
# #     "G1+TG1":[("TUE",2),("THU",3),("MON",5)],
# #     "A2+TA2":[("MON",6),("WED",7),("FRI",9)],
# #     "B2+TB2":[("TUE",6),("THU",7),("MON",9)],
# #     "C2+TC2":[("WED",6),("FRI",7),("TUE",9)],
# #     "D2+TD2":[("THU",6),("MON",8),("WED",9)],
# #     "E2+TE2":[("FRI",6),("TUE",8),("THU",9)],
# #     "F2+TF2":[("MON",7),("WED",8),("FRI",10)],
# #     "G2+TG2":[("TUE",7),("THU",8),("MON",10)],
# #     "A1+TA1+TAA1":[("MON",1),("WED",2),("FRI",3),("TUE",5)],
# #     "B1+TB1+TBB1":[("TUE",1),("THU",2),("MON",4),("WED",5)],
# #     "C1+TC1+TCC1":[("WED",1),("FRI",2),("TUE",4),("THU",5)],
# #     "D1+TD1+TDD1":[("THU",1),("MON",3),("FRI",5),("WED",4)],
# #     "A2+TA2+TAA2":[("MON",6),("WED",7),("FRI",9),("TUE",10)],
# #     "B2+TB2+TBB2":[("TUE",6),("THU",7),("MON",9),("WED",10)],
# #     "C2+TC2+TCC2":[("WED",6),("FRI",7),("TUE",9),("THU",10)],
# #     "D2+TD2+TDD2":[("THU",6),("MON",8),("WED",9),("FRI",11)],
# # }

# # # Morning = suffix 1, Evening = suffix 2
# # MORNING_BUNDLES = {k: v for k, v in SLOT_BUNDLES.items() if "1" in k.split("+")[0][-1]}
# # EVENING_BUNDLES = {k: v for k, v in SLOT_BUNDLES.items() if "2" in k.split("+")[0][-1]}

# # VALID_BUNDLES_BY_SESSIONS = {
# #     2: ["A1","B1","C1","D1","E1","F1","G1",
# #         "A2","B2","C2","D2","E2","F2","G2"],
# #     3: ["A1+TA1","B1+TB1","C1+TC1","D1+TD1","E1+TE1","F1+TF1","G1+TG1",
# #         "A2+TA2","B2+TB2","C2+TC2","D2+TD2","E2+TE2","F2+TF2","G2+TG2"],
# #     4: ["A1+TA1+TAA1","B1+TB1+TBB1","C1+TC1+TCC1","D1+TD1+TDD1",
# #         "A2+TA2+TAA2","B2+TB2+TBB2","C2+TC2+TCC2","D2+TD2+TDD2"],
# # }

# # MORNING_BY_SESSIONS = {
# #     sess: [b for b in bundles if b in MORNING_BUNDLES]
# #     for sess, bundles in VALID_BUNDLES_BY_SESSIONS.items()
# # }
# # EVENING_BY_SESSIONS = {
# #     sess: [b for b in bundles if b in EVENING_BUNDLES]
# #     for sess, bundles in VALID_BUNDLES_BY_SESSIONS.items()
# # }

# # # ══════════════════════════════════════════════════════════════════
# # # OVERLAP PRECOMPUTATION (theory only)
# # # ══════════════════════════════════════════════════════════════════

# # def _theory_windows(name):
# #     return [(d, *THEORY_PERIOD_TIMES[p]) for d, p in SLOT_BUNDLES[name]]

# # def _windows_overlap(w1, w2):
# #     for d1, s1, e1 in w1:
# #         for d2, s2, e2 in w2:
# #             if d1 == d2 and max(s1,s2) < min(e1,e2):
# #                 return True
# #     return False

# # print("Precomputing theory slot overlap table...")
# # ALL_THEORY_SLOTS = list(SLOT_BUNDLES.keys())
# # ALL_WINDOWS = {s: _theory_windows(s) for s in ALL_THEORY_SLOTS}
# # SLOT_OVERLAP = {
# #     (a, b): _windows_overlap(ALL_WINDOWS[a], ALL_WINDOWS[b])
# #     for a in ALL_THEORY_SLOTS for b in ALL_THEORY_SLOTS
# # }
# # sc = lambda a, b: SLOT_OVERLAP[(a, b)]
# # print("Done.\n")

# # # ══════════════════════════════════════════════════════════════════
# # # LOAD DATA
# # # ══════════════════════════════════════════════════════════════════

# # with open("data/courses.json") as f: courses_raw = json.load(f)["courses"]
# # with open("data/recs.json")    as f: students    = json.load(f)["students"]
# # N_STUDENTS = len(students)

# # course_map = {c["course_code"]: c for c in courses_raw}

# # def get_sessions(code):
# #     c = course_map.get(code)
# #     return (c.get("L", 0) + c.get("T", 0)) if c else None

# # # ══════════════════════════════════════════════════════════════════
# # # COURSE CLASSIFICATION — theory only
# # # ══════════════════════════════════════════════════════════════════

# # all_courses = set(c for s in students for c in s["recommended_courses"])

# # # Only schedulable theory courses (has valid bundles)
# # theory_courses = set()
# # for code in all_courses:
# #     if code.endswith("P"):
# #         continue
# #     sess = get_sessions(code)
# #     if sess and MORNING_BY_SESSIONS.get(sess) and EVENING_BY_SESSIONS.get(sess):
# #         theory_courses.add(code)

# # course_demand = Counter(c for s in students
# #                         for c in s["recommended_courses"] if c in theory_courses)

# # print(f"Schedulable theory courses: {len(theory_courses)}")
# # print(f"Students: {N_STUDENTS}\n")

# # # ══════════════════════════════════════════════════════════════════
# # # STUDENT COURSE LISTS (theory only)
# # # ══════════════════════════════════════════════════════════════════

# # student_theory_courses = {}
# # for s in students:
# #     tc = [c for c in s["recommended_courses"] if c in theory_courses]
# #     student_theory_courses[s["student_id"]] = tc

# # students_by_id = {s["student_id"]: s for s in students}

# # # ══════════════════════════════════════════════════════════════════
# # # OBJECTIVE FUNCTION
# # # ══════════════════════════════════════════════════════════════════

# # def student_has_conflict_free_option(courses, asgn):
# #     """
# #     Check if a student with given theory courses can pick
# #     morning or evening for each course without any overlap.
# #     asgn: {course: (morning_slot, evening_slot)}
# #     Returns True if at least one conflict-free combo exists.
# #     """
# #     if not courses:
# #         return True
# #     n = len(courses)
# #     # For each course, options are [morning_slot, evening_slot]
# #     options = [(asgn[c][0], asgn[c][1]) for c in courses]

# #     # Enumerate all 2^n combinations
# #     for combo in product(*[[0, 1]] * n):
# #         slots = [options[i][combo[i]] for i in range(n)]
# #         conflict = False
# #         for i in range(n):
# #             for j in range(i+1, n):
# #                 if sc(slots[i], slots[j]):
# #                     conflict = True
# #                     break
# #             if conflict:
# #                 break
# #         if not conflict:
# #             return True
# #     return False

# # def count_unsolvable_students(asgn):
# #     """Count students with no conflict-free section combination."""
# #     count = 0
# #     for s in students:
# #         sid  = s["student_id"]
# #         courses = [c for c in student_theory_courses[sid] if c in asgn]
# #         if not courses:
# #             continue
# #         if not student_has_conflict_free_option(courses, asgn):
# #             count += 1
# #     return count

# # def best_section_for_student(sid, asgn):
# #     """
# #     Find the best (minimum clashes) section combo for a student.
# #     Returns: (best_combo_dict, n_clashes)
# #     combo_dict: {course: 'morning'|'evening', slot: ...}
# #     """
# #     courses = [c for c in student_theory_courses[sid] if c in asgn]
# #     if not courses:
# #         return {}, 0

# #     n = len(courses)
# #     options = [(asgn[c][0], asgn[c][1]) for c in courses]
# #     best_combo = None
# #     best_clashes = float("inf")

# #     for combo in product(*[[0, 1]] * n):
# #         slots = [options[i][combo[i]] for i in range(n)]
# #         clashes = sum(
# #             1 for i in range(n) for j in range(i+1, n)
# #             if sc(slots[i], slots[j])
# #         )
# #         if clashes < best_clashes:
# #             best_clashes = clashes
# #             best_combo   = combo
# #         if best_clashes == 0:
# #             break

# #     result = {}
# #     for i, c in enumerate(courses):
# #         choice = best_combo[i]
# #         result[c] = {
# #             "section": "morning" if choice == 0 else "evening",
# #             "slot":    options[i][choice]
# #         }
# #     return result, best_clashes

# # # ══════════════════════════════════════════════════════════════════
# # # PHASE 1 — RANDOM INITIALISATION
# # # ══════════════════════════════════════════════════════════════════

# # print("=" * 65)
# # print("  PHASE 1 — Random Initialisation (two sections per course)")
# # print("=" * 65)

# # def random_assign():
# #     asgn = {}
# #     for code in theory_courses:
# #         sess = get_sessions(code)
# #         m_opts = MORNING_BY_SESSIONS.get(sess, [])
# #         e_opts = EVENING_BY_SESSIONS.get(sess, [])
# #         if not m_opts or not e_opts:
# #             continue
# #         asgn[code] = (random.choice(m_opts), random.choice(e_opts))
# #     return asgn

# # asgn = random_assign()
# # p1_unsolvable = count_unsolvable_students(asgn)
# # p1_cf = (N_STUDENTS - p1_unsolvable) / N_STUDENTS * 100
# # print(f"[P1] Assigned: {len(asgn)} courses")
# # print(f"[P1] Unsolvable students: {p1_unsolvable}/{N_STUDENTS} ({p1_cf:.1f}% solvable)\n")

# # # ══════════════════════════════════════════════════════════════════
# # # CONFLICT GRAPH (for biased sampling)
# # # ══════════════════════════════════════════════════════════════════

# # adj = defaultdict(dict)
# # for s in students:
# #     cs = [c for c in s["recommended_courses"] if c in theory_courses]
# #     for ca, cb in combinations(cs, 2):
# #         adj[ca][cb] = adj[ca].get(cb, 0) + 1
# #         adj[cb][ca] = adj[cb].get(ca, 0) + 1

# # weighted_degree = {c: sum(adj[c].values()) for c in theory_courses}

# # # ══════════════════════════════════════════════════════════════════
# # # CACHE: which students are currently unsolvable
# # # ══════════════════════════════════════════════════════════════════

# # def build_unsolvable_cache(asgn):
# #     """Returns set of student IDs that are currently unsolvable."""
# #     unsolvable = set()
# #     for s in students:
# #         sid = s["student_id"]
# #         courses = [c for c in student_theory_courses[sid] if c in asgn]
# #         if not courses:
# #             continue
# #         if not student_has_conflict_free_option(courses, asgn):
# #             unsolvable.add(sid)
# #     return unsolvable

# # def delta_move(asgn, course, new_m, new_e, unsolvable_set):
# #     """
# #     Compute change in unsolvable count if we change course's slots.
# #     Only recheck students who take this course.
# #     Returns: (new_unsolvable_count_change, affected_students)
# #     """
# #     old_m, old_e = asgn[course]
# #     if new_m == old_m and new_e == old_e:
# #         return 0, set()

# #     affected = set(s["student_id"] for s in students
# #                    if course in student_theory_courses[s["student_id"]])

# #     # Tentatively apply move
# #     asgn[course] = (new_m, new_e)

# #     gained = 0  # newly solvable
# #     lost   = 0  # newly unsolvable

# #     for sid in affected:
# #         courses = [c for c in student_theory_courses[sid] if c in asgn]
# #         was_unsolvable = sid in unsolvable_set
# #         now_unsolvable = not student_has_conflict_free_option(courses, asgn)

# #         if was_unsolvable and not now_unsolvable:
# #             gained += 1
# #         elif not was_unsolvable and now_unsolvable:
# #             lost += 1

# #     # Revert
# #     asgn[course] = (old_m, old_e)

# #     return lost - gained, affected  # positive = worse, negative = better

# # # ══════════════════════════════════════════════════════════════════
# # # SA RUNNER
# # # ══════════════════════════════════════════════════════════════════

# # def geometric_schedule(T_start, T_end, n):
# #     if n <= 1: return [T_start]
# #     f = (T_end / T_start) ** (1.0 / max(n-1, 1))
# #     return [T_start * (f**i) for i in range(n)]

# # def run_sa(start_asgn, iterations, T_start, T_end,
# #            tag="SA", reheat_thresh=8000, reheat_T_frac=0.20):

# #     current       = {c: (m, e) for c, (m, e) in start_asgn.items()}
# #     unsolvable    = build_unsolvable_cache(current)
# #     best_r        = len(unsolvable)
# #     best_a        = {c: (m, e) for c, (m, e) in current.items()}
# #     temps         = geometric_schedule(T_start, T_end, iterations)
# #     n_reheats     = 0
# #     last_best_iter = 0
# #     t0 = time.time()

# #     courses_list = list(current.keys())

# #     for it in range(iterations):
# #         T = temps[it]

# #         # Reheat on stagnation
# #         if it - last_best_iter >= reheat_thresh and T < 1.0 and n_reheats < 5:
# #             reheat_T  = reheat_T_frac * T_start
# #             remaining = iterations - it
# #             if remaining > 1:
# #                 temps[it:] = geometric_schedule(reheat_T, T_end, remaining)
# #                 T = temps[it]
# #                 n_reheats += 1
# #                 last_best_iter = it
# #                 print(f"    [{tag}] iter {it+1} → REHEAT #{n_reheats} "
# #                       f"T={reheat_T:.1f}  best={best_r}")

# #         # Pick a course biased toward high weighted-degree
# #         # (courses taken by many students together = higher conflict potential)
# #         c = random.choices(
# #             courses_list,
# #             weights=[weighted_degree.get(x, 1) for x in courses_list]
# #         )[0]

# #         sess   = get_sessions(c)
# #         m_opts = MORNING_BY_SESSIONS.get(sess, [])
# #         e_opts = EVENING_BY_SESSIONS.get(sess, [])
# #         if not m_opts or not e_opts:
# #             continue

# #         # Randomly change morning, evening, or both
# #         r = random.random()
# #         old_m, old_e = current[c]
# #         if r < 0.40:
# #             new_m = random.choice(m_opts)
# #             new_e = old_e
# #         elif r < 0.80:
# #             new_m = old_m
# #             new_e = random.choice(e_opts)
# #         else:
# #             new_m = random.choice(m_opts)
# #             new_e = random.choice(e_opts)

# #         if new_m == old_m and new_e == old_e:
# #             continue

# #         delta, affected = delta_move(current, c, new_m, new_e, unsolvable)

# #         if delta < 0 or random.random() < math.exp(-delta / T):
# #             # Apply move
# #             current[c] = (new_m, new_e)

# #             # Update unsolvable cache for affected students
# #             for sid in affected:
# #                 courses = [cc for cc in student_theory_courses[sid] if cc in current]
# #                 if not student_has_conflict_free_option(courses, current):
# #                     unsolvable.add(sid)
# #                 else:
# #                     unsolvable.discard(sid)

# #             real = len(unsolvable)
# #             if real < best_r:
# #                 best_r = real
# #                 best_a = {c: (m, e) for c, (m, e) in current.items()}
# #                 last_best_iter = it

# #         if (it + 1) % 1000 == 0:
# #             print(f"    [{tag}] iter {it+1:6d} | T={T:7.3f} | "
# #                   f"unsolvable={len(unsolvable)} best={best_r} | "
# #                   f"reheats={n_reheats} | {time.time()-t0:.1f}s")

# #     return best_a, best_r

# # # ══════════════════════════════════════════════════════════════════
# # # PHASE 2 — SA OPTIMISATION
# # # ══════════════════════════════════════════════════════════════════

# # print("\n" + "=" * 65)
# # print("  PHASE 2 — SA Optimiser (two-section theory assignment)")
# # print("=" * 65)

# # T_START    = 50.0
# # T_END      = 0.01
# # ITERS      = 50000
# # N_RESTARTS = 4

# # best_ever       = {c: (m, e) for c, (m, e) in asgn.items()}
# # best_ever_score = p1_unsolvable

# # for restart in range(N_RESTARTS):
# #     print(f"\n  [R{restart+1}] Starting restart {restart+1}/{N_RESTARTS} ...")

# #     if restart == 0:
# #         start = {c: (m, e) for c, (m, e) in best_ever.items()}
# #     else:
# #         # Perturb best
# #         start = {c: (m, e) for c, (m, e) in best_ever.items()}
# #         frac  = [0.15, 0.25, 0.35][restart % 3]
# #         n_p   = max(1, int(len(start) * frac))
# #         for c in random.sample(list(start.keys()), n_p):
# #             sess   = get_sessions(c)
# #             m_opts = MORNING_BY_SESSIONS.get(sess, [])
# #             e_opts = EVENING_BY_SESSIONS.get(sess, [])
# #             if m_opts and e_opts:
# #                 start[c] = (random.choice(m_opts), random.choice(e_opts))
# #         print(f"  [R{restart+1}] Perturbed ({frac:.0%}): "
# #               f"{count_unsolvable_students(start)} unsolvable")

# #     ra, rs = run_sa(start, ITERS, T_START, T_END,
# #                     tag=f"R{restart+1}",
# #                     reheat_thresh=6000, reheat_T_frac=0.25)

# #     if rs < best_ever_score:
# #         best_ever_score = rs
# #         best_ever = {c: (m, e) for c, (m, e) in ra.items()}

# #     print(f"  [R{restart+1}] unsolvable={rs}  global_best={best_ever_score}")

# # final_asgn  = best_ever
# # final_score = best_ever_score
# # final_cf    = (N_STUDENTS - final_score) / N_STUDENTS * 100

# # print(f"\n[FINAL] Unsolvable students: {final_score}/{N_STUDENTS} "
# #       f"({final_cf:.1f}% fully solvable)")

# # # ══════════════════════════════════════════════════════════════════
# # # PHASE 3 — PER-STUDENT OPTIMAL SECTION ASSIGNMENT
# # # ══════════════════════════════════════════════════════════════════

# # print("\n[Phase 3] Computing optimal section assignments per student...")

# # student_results = {}
# # for s in students:
# #     sid   = s["student_id"]
# #     combo, clashes = best_section_for_student(sid, final_asgn)
# #     student_results[sid] = {
# #         "name":       s["name"],
# #         "clashes":    clashes,
# #         "selection":  combo,
# #         "solvable":   clashes == 0
# #     }

# # n_solvable = sum(1 for v in student_results.values() if v["solvable"])
# # print(f"[Phase 3] Students with zero-conflict timetable: "
# #       f"{n_solvable}/{N_STUDENTS}")

# # # Top 10 most-conflicted students (who benefit most from section advice)
# # top10 = sorted(
# #     [(sid, v) for sid, v in student_results.items()],
# #     key=lambda x: x[1]["clashes"],
# #     reverse=True
# # )[:10]

# # # ══════════════════════════════════════════════════════════════════
# # # SAVE OUTPUT
# # # ══════════════════════════════════════════════════════════════════

# # output = {
# #     "timetable": {
# #         c: {"morning": m, "evening": e}
# #         for c, (m, e) in final_asgn.items()
# #     },
# #     "metrics": {
# #         "total_courses":       len(final_asgn),
# #         "total_students":      N_STUDENTS,
# #         "unsolvable_students": final_score,
# #         "solvable_students":   N_STUDENTS - final_score,
# #         "solvable_pct":        round(final_cf, 2),
# #     },
# #     "student_sections": {
# #         sid: {
# #             "name":     v["name"],
# #             "clashes":  v["clashes"],
# #             "solvable": v["solvable"],
# #             "selection": {
# #                 c: {"section": info["section"], "slot": info["slot"]}
# #                 for c, info in v["selection"].items()
# #             }
# #         }
# #         for sid, v in student_results.items()
# #     }
# # }

# # with open("data/two_section_timetable.json", "w") as f:
# #     json.dump(output, f, indent=2)

# # print("\n[DONE] Saved → data/two_section_timetable.json")
# # print(f"       Unsolvable: {final_score}/{N_STUDENTS} | "
# #       f"Solvable: {N_STUDENTS-final_score}/{N_STUDENTS} ({final_cf:.1f}%)")
# """
# FFCS VIT Chennai — Two-Section SA (Theory + Lab, Two-Phase)
# ============================================================
# Phase 1 : SA optimises theory slot assignment only (fast).
# Phase 2 : SA optimises lab slot assignment with theory slots FIXED.
# Phase 3 : Per-student optimal section assignment
#           (pure morning preferred, pure evening second, mixed fallback).

# Early stopping: if unsolvable == 0 at any point, halt immediately.
# """

# import json, math, random, time
# from collections import defaultdict
# from itertools import combinations, product

# random.seed(42)

# # ══════════════════════════════════════════════════════════════════
# # SLOT DATA
# # ══════════════════════════════════════════════════════════════════

# THEORY_PERIOD_TIMES = {
#     1:(480,530),  2:(535,585),  3:(590,640),  4:(705,750),
#     5:(755,805),  6:(840,890),  7:(895,945),  8:(950,1000),
#     9:(1005,1055),10:(1060,1110),11:(1115,1165)
# }

# SLOT_BUNDLES = {
#     "A1":[("MON",1),("WED",2)],  "B1":[("TUE",1),("THU",2)],
#     "C1":[("WED",1),("FRI",2)],  "D1":[("THU",1),("MON",3)],
#     "E1":[("FRI",1),("TUE",3)],  "F1":[("MON",2),("WED",3)],
#     "G1":[("TUE",2),("THU",3)],
#     "A2":[("MON",6),("WED",7)],  "B2":[("TUE",6),("THU",7)],
#     "C2":[("WED",6),("FRI",7)],  "D2":[("THU",6),("MON",8)],
#     "E2":[("FRI",6),("TUE",8)],  "F2":[("MON",7),("WED",8)],
#     "G2":[("TUE",7),("THU",8)],
#     "A1+TA1":[("MON",1),("WED",2),("FRI",3)],
#     "B1+TB1":[("TUE",1),("THU",2),("MON",4)],
#     "C1+TC1":[("WED",1),("FRI",2),("TUE",4)],
#     "D1+TD1":[("THU",1),("MON",3),("FRI",5)],
#     "E1+TE1":[("FRI",1),("TUE",3),("THU",4)],
#     "F1+TF1":[("MON",2),("WED",3),("FRI",4)],
#     "G1+TG1":[("TUE",2),("THU",3),("MON",5)],
#     "A2+TA2":[("MON",6),("WED",7),("FRI",9)],
#     "B2+TB2":[("TUE",6),("THU",7),("MON",9)],
#     "C2+TC2":[("WED",6),("FRI",7),("TUE",9)],
#     "D2+TD2":[("THU",6),("MON",8),("WED",9)],
#     "E2+TE2":[("FRI",6),("TUE",8),("THU",9)],
#     "F2+TF2":[("MON",7),("WED",8),("FRI",10)],
#     "G2+TG2":[("TUE",7),("THU",8),("MON",10)],
#     "A1+TA1+TAA1":[("MON",1),("WED",2),("FRI",3),("TUE",5)],
#     "B1+TB1+TBB1":[("TUE",1),("THU",2),("MON",4),("WED",5)],
#     "C1+TC1+TCC1":[("WED",1),("FRI",2),("TUE",4),("THU",5)],
#     "D1+TD1+TDD1":[("THU",1),("MON",3),("FRI",5),("WED",4)],
#     "A2+TA2+TAA2":[("MON",6),("WED",7),("FRI",9),("TUE",10)],
#     "B2+TB2+TBB2":[("TUE",6),("THU",7),("MON",9),("WED",10)],
#     "C2+TC2+TCC2":[("WED",6),("FRI",7),("TUE",9),("THU",10)],
#     "D2+TD2+TDD2":[("THU",6),("MON",8),("WED",9),("FRI",11)],
# }

# MORNING_BUNDLES = {k: v for k, v in SLOT_BUNDLES.items() if "1" in k.split("+")[0][-1]}
# EVENING_BUNDLES = {k: v for k, v in SLOT_BUNDLES.items() if "2" in k.split("+")[0][-1]}

# VALID_BUNDLES_BY_SESSIONS = {
#     2: ["A1","B1","C1","D1","E1","F1","G1",
#         "A2","B2","C2","D2","E2","F2","G2"],
#     3: ["A1+TA1","B1+TB1","C1+TC1","D1+TD1","E1+TE1","F1+TF1","G1+TG1",
#         "A2+TA2","B2+TB2","C2+TC2","D2+TD2","E2+TE2","F2+TF2","G2+TG2"],
#     4: ["A1+TA1+TAA1","B1+TB1+TBB1","C1+TC1+TCC1","D1+TD1+TDD1",
#         "A2+TA2+TAA2","B2+TB2+TBB2","C2+TC2+TCC2","D2+TD2+TDD2"],
# }

# MORNING_BY_SESSIONS = {
#     sess: [b for b in bundles if b in MORNING_BUNDLES]
#     for sess, bundles in VALID_BUNDLES_BY_SESSIONS.items()
# }
# EVENING_BY_SESSIONS = {
#     sess: [b for b in bundles if b in EVENING_BUNDLES]
#     for sess, bundles in VALID_BUNDLES_BY_SESSIONS.items()
# }

# # ══════════════════════════════════════════════════════════════════
# # LAB SLOT DATA
# # ══════════════════════════════════════════════════════════════════

# LAB_SLOT_MAP = {
#     "L1":("MON",1),  "L2":("MON",1),
#     "L3":("MON",2),  "L4":("MON",2),
#     "L5":("MON",3),  "L6":("MON",3),
#     "L7":("TUE",1),  "L8":("TUE",1),
#     "L9":("TUE",2),  "L10":("TUE",2),
#     "L11":("TUE",3), "L12":("TUE",3),
#     "L13":("WED",1), "L14":("WED",1),
#     "L15":("WED",2), "L16":("WED",2),
#     "L19":("THU",1), "L20":("THU",1),
#     "L21":("THU",2), "L22":("THU",2),
#     "L23":("THU",3), "L24":("THU",3),
#     "L25":("FRI",1), "L26":("FRI",1),
#     "L27":("FRI",2), "L28":("FRI",2),
#     "L29":("FRI",3), "L30":("FRI",3),
#     "L31":("MON",6), "L32":("MON",6),
#     "L33":("MON",7), "L34":("MON",7),
#     "L35":("MON",8), "L36":("MON",8),
#     "L37":("TUE",6), "L38":("TUE",6),
#     "L39":("TUE",7), "L40":("TUE",7),
#     "L41":("TUE",8), "L42":("TUE",8),
#     "L43":("WED",6), "L44":("WED",6),
#     "L45":("WED",7), "L46":("WED",7),
#     "L47":("WED",8), "L48":("WED",8),
#     "L49":("THU",6), "L50":("THU",6),
#     "L51":("THU",7), "L52":("THU",7),
#     "L53":("THU",8), "L54":("THU",8),
#     "L55":("FRI",6), "L56":("FRI",6),
#     "L57":("FRI",7), "L58":("FRI",7),
#     "L59":("FRI",8), "L60":("FRI",8),
# }

# def _build_lab_pairs():
#     all_slots = sorted(LAB_SLOT_MAP.keys(), key=lambda x: int(x[1:]))
#     morning_pairs, evening_pairs = [], []
#     i = 0
#     while i < len(all_slots) - 1:
#         s1, s2 = all_slots[i], all_slots[i+1]
#         n1, n2 = int(s1[1:]), int(s2[1:])
#         if n2 == n1 + 1 and LAB_SLOT_MAP[s1] == LAB_SLOT_MAP[s2]:
#             pair = f"{s1}+{s2}"
#             (morning_pairs if n1 <= 30 else evening_pairs).append(pair)
#             i += 2
#         else:
#             i += 1
#     return morning_pairs, evening_pairs

# MORNING_LAB_PAIRS, EVENING_LAB_PAIRS = _build_lab_pairs()

# def _build_p4_bundles(pairs):
#     bundles = []
#     for p1, p2 in combinations(pairs, 2):
#         d1 = LAB_SLOT_MAP[p1.split("+")[0]][0]
#         d2 = LAB_SLOT_MAP[p2.split("+")[0]][0]
#         if d1 != d2:
#             n1 = int(p1.split("+")[0][1:])
#             n2 = int(p2.split("+")[0][1:])
#             bundles.append(f"{p1}+{p2}" if n1 < n2 else f"{p2}+{p1}")
#     return bundles

# MORNING_P4_BUNDLES = _build_p4_bundles(MORNING_LAB_PAIRS)
# EVENING_P4_BUNDLES = _build_p4_bundles(EVENING_LAB_PAIRS)

# LAB_MORNING_BY_P = {2: MORNING_LAB_PAIRS, 4: MORNING_P4_BUNDLES}
# LAB_EVENING_BY_P = {2: EVENING_LAB_PAIRS, 4: EVENING_P4_BUNDLES}

# print(f"P=2 morning lab pairs  : {len(MORNING_LAB_PAIRS)}")
# print(f"P=2 evening lab pairs  : {len(EVENING_LAB_PAIRS)}")
# print(f"P=4 morning lab bundles: {len(MORNING_P4_BUNDLES)}")
# print(f"P=4 evening lab bundles: {len(EVENING_P4_BUNDLES)}")

# # ══════════════════════════════════════════════════════════════════
# # OVERLAP PRECOMPUTATION
# # ══════════════════════════════════════════════════════════════════

# def _theory_windows(name):
#     return [(d, *THEORY_PERIOD_TIMES[p]) for d, p in SLOT_BUNDLES[name]]

# def _lab_windows(bundle_str):
#     windows = []
#     for slot in bundle_str.split("+"):
#         day, period = LAB_SLOT_MAP[slot]
#         s, e = THEORY_PERIOD_TIMES[period]
#         windows.append((day, s, e))
#     return windows

# def _windows_overlap(w1, w2):
#     for d1, s1, e1 in w1:
#         for d2, s2, e2 in w2:
#             if d1 == d2 and max(s1, s2) < min(e1, e2):
#                 return True
#     return False

# print("\nPrecomputing overlap tables...")

# ALL_THEORY_SLOTS   = list(SLOT_BUNDLES.keys())
# ALL_THEORY_WINDOWS = {s: _theory_windows(s) for s in ALL_THEORY_SLOTS}
# ALL_LAB_BUNDLES    = (MORNING_LAB_PAIRS + EVENING_LAB_PAIRS +
#                       MORNING_P4_BUNDLES + EVENING_P4_BUNDLES)
# ALL_LAB_WINDOWS    = {b: _lab_windows(b) for b in ALL_LAB_BUNDLES}

# TT_OVERLAP = {(a,b): _windows_overlap(ALL_THEORY_WINDOWS[a], ALL_THEORY_WINDOWS[b])
#               for a in ALL_THEORY_SLOTS for b in ALL_THEORY_SLOTS}
# TL_OVERLAP = {(t,l): _windows_overlap(ALL_THEORY_WINDOWS[t], ALL_LAB_WINDOWS[l])
#               for t in ALL_THEORY_SLOTS for l in ALL_LAB_BUNDLES}
# LL_OVERLAP = {(a,b): _windows_overlap(ALL_LAB_WINDOWS[a], ALL_LAB_WINDOWS[b])
#               for a in ALL_LAB_BUNDLES for b in ALL_LAB_BUNDLES}

# sc          = lambda a, b: TT_OVERLAP[(a, b)]
# tt_conflict = lambda a, b: TT_OVERLAP[(a, b)]
# tl_conflict = lambda t, l: TL_OVERLAP[(t, l)]
# ll_conflict = lambda a, b: LL_OVERLAP[(a, b)]

# print("Done.\n")

# # ══════════════════════════════════════════════════════════════════
# # LOAD DATA
# # ══════════════════════════════════════════════════════════════════

# with open("data/courses.json") as f: courses_raw = json.load(f)["courses"]
# with open("data/recs.json")    as f: students    = json.load(f)["students"]
# N_STUDENTS = len(students)

# course_map = {c["course_code"]: c for c in courses_raw}

# def get_sessions(code):
#     c = course_map.get(code)
#     return (c.get("L", 0) + c.get("T", 0)) if c else None

# def get_lab_p(code):
#     c = course_map.get(code)
#     return c.get("P", 0) if c else 0

# # ══════════════════════════════════════════════════════════════════
# # COURSE CLASSIFICATION
# # ══════════════════════════════════════════════════════════════════

# all_codes = set(c for s in students for c in s["recommended_courses"])

# theory_courses = set()
# for code in all_codes:
#     c = course_map.get(code)
#     if c is None: continue
#     if c.get("is_lab", False): continue
#     if c.get("embedded_lab", False): continue
#     sess = get_sessions(code)
#     if sess and MORNING_BY_SESSIONS.get(sess) and EVENING_BY_SESSIONS.get(sess):
#         theory_courses.add(code)

# lab_courses = set()
# for code in all_codes:
#     c = course_map.get(code)
#     if c is None: continue
#     if not c.get("is_lab", False): continue
#     p = c.get("P", 0)
#     if p not in (2, 4): continue
#     if not LAB_MORNING_BY_P.get(p) or not LAB_EVENING_BY_P.get(p): continue
#     lab_courses.add(code)

# lab_to_theory = {}
# for code in lab_courses:
#     tc = course_map[code].get("theory_course_code")
#     if tc:
#         lab_to_theory[code] = tc

# theory_to_lab = {v: k for k, v in lab_to_theory.items() if k in lab_courses}

# print(f"Schedulable theory courses : {len(theory_courses)}")
# print(f"Linked lab courses         : {len(lab_courses)}")
# print(f"Students                   : {N_STUDENTS}\n")

# # ══════════════════════════════════════════════════════════════════
# # STUDENT COURSE LISTS
# # ══════════════════════════════════════════════════════════════════

# student_theory_courses = {}
# student_lab_courses    = {}
# for s in students:
#     sid = s["student_id"]
#     student_theory_courses[sid] = [c for c in s["recommended_courses"] if c in theory_courses]
#     student_lab_courses[sid]    = [c for c in s["recommended_courses"] if c in lab_courses]

# # ══════════════════════════════════════════════════════════════════
# # CONFLICT-FREE CHECK
# # ══════════════════════════════════════════════════════════════════

# def student_has_conflict_free_option(sid, t_asgn, l_asgn):
#     tcourses = [c for c in student_theory_courses[sid] if c in t_asgn]
#     lcourses = [c for c in student_lab_courses[sid]    if c in l_asgn]
#     nt, nl   = len(tcourses), len(lcourses)
#     if nt + nl == 0:
#         return True
#     t_opts = [(t_asgn[c][0], t_asgn[c][1]) for c in tcourses]
#     l_opts = [(l_asgn[c][0], l_asgn[c][1]) for c in lcourses]
#     for combo in product(*[[0, 1]] * (nt + nl)):
#         t_combo = combo[:nt]; l_combo = combo[nt:]
#         t_slots = [t_opts[i][t_combo[i]] for i in range(nt)]
#         l_slots = [l_opts[i][l_combo[i]] for i in range(nl)]
#         conflict = False
#         for i in range(nt):
#             for j in range(i+1, nt):
#                 if tt_conflict(t_slots[i], t_slots[j]): conflict = True; break
#             if conflict: break
#         if not conflict:
#             for i in range(nl):
#                 for j in range(i+1, nl):
#                     if ll_conflict(l_slots[i], l_slots[j]): conflict = True; break
#                 if conflict: break
#         if not conflict:
#             for ti, ts in enumerate(t_slots):
#                 for li, ls in enumerate(l_slots):
#                     if lab_to_theory.get(lcourses[li]) == tcourses[ti]: continue
#                     if tl_conflict(ts, ls): conflict = True; break
#                 if conflict: break
#         if not conflict:
#             for ti, tc in enumerate(tcourses):
#                 lab_code = theory_to_lab.get(tc)
#                 if lab_code and lab_code in lcourses:
#                     li = lcourses.index(lab_code)
#                     if tl_conflict(t_slots[ti], l_slots[li]): conflict = True; break
#         if not conflict:
#             return True
#     return False

# # ══════════════════════════════════════════════════════════════════
# # THEORY SA COMPONENTS
# # ══════════════════════════════════════════════════════════════════

# def build_theory_unsolvable_cache(asgn):
#     unsolvable = set()
#     for s in students:
#         sid     = s["student_id"]
#         courses = [c for c in student_theory_courses[sid] if c in asgn]
#         if not courses: continue
#         n    = len(courses)
#         opts = [(asgn[c][0], asgn[c][1]) for c in courses]
#         for combo in product(*[[0, 1]] * n):
#             slots    = [opts[i][combo[i]] for i in range(n)]
#             conflict = any(sc(slots[i], slots[j])
#                            for i in range(n) for j in range(i+1, n))
#             if not conflict: break
#         else:
#             unsolvable.add(sid)
#     return unsolvable

# def delta_move_theory(asgn, course, new_m, new_e, unsolvable_set):
#     old_m, old_e = asgn[course]
#     if new_m == old_m and new_e == old_e:
#         return 0, set()
#     affected = set(s["student_id"] for s in students
#                    if course in student_theory_courses[s["student_id"]])
#     asgn[course] = (new_m, new_e)
#     gained = lost = 0
#     for sid in affected:
#         courses  = [c for c in student_theory_courses[sid] if c in asgn]
#         n        = len(courses)
#         opts     = [(asgn[c][0], asgn[c][1]) for c in courses]
#         solvable = False
#         for combo in product(*[[0, 1]] * n):
#             slots    = [opts[i][combo[i]] for i in range(n)]
#             conflict = any(sc(slots[i], slots[j])
#                            for i in range(n) for j in range(i+1, n))
#             if not conflict: solvable = True; break
#         was = sid in unsolvable_set
#         now = not solvable
#         if was and not now: gained += 1
#         elif not was and now: lost  += 1
#     asgn[course] = (old_m, old_e)
#     return lost - gained, affected

# adj = defaultdict(dict)
# for s in students:
#     cs = [c for c in s["recommended_courses"] if c in theory_courses]
#     for ca, cb in combinations(cs, 2):
#         adj[ca][cb] = adj[ca].get(cb, 0) + 1
#         adj[cb][ca] = adj[cb].get(ca, 0) + 1

# theory_weighted_degree = {c: sum(adj[c].values()) for c in theory_courses}

# lab_enrollment = {
#     lc: sum(1 for s in students if lc in student_lab_courses[s["student_id"]])
#     for lc in lab_courses
# }

# def geometric_schedule(T_start, T_end, n):
#     if n <= 1: return [T_start]
#     f = (T_end / T_start) ** (1.0 / max(n-1, 1))
#     return [T_start * (f**i) for i in range(n)]

# # ══════════════════════════════════════════════════════════════════
# # THEORY SA RUNNER
# # ══════════════════════════════════════════════════════════════════

# def run_theory_sa(start_asgn, iterations, T_start, T_end,
#                   tag="SA", reheat_thresh=8000, reheat_T_frac=0.20):
#     current        = dict(start_asgn)
#     unsolvable     = build_theory_unsolvable_cache(current)
#     best_r         = len(unsolvable)
#     best_a         = dict(current)
#     temps          = geometric_schedule(T_start, T_end, iterations)
#     n_reheats      = 0
#     last_best_iter = 0
#     t0             = time.time()
#     courses_list   = list(current.keys())

#     for it in range(iterations):
#         T = temps[it]
#         if it - last_best_iter >= reheat_thresh and T < 1.0 and n_reheats < 5:
#             reheat_T  = reheat_T_frac * T_start
#             remaining = iterations - it
#             if remaining > 1:
#                 temps[it:] = geometric_schedule(reheat_T, T_end, remaining)
#                 T = temps[it]
#                 n_reheats     += 1
#                 last_best_iter = it
#                 print(f"    [{tag}] iter {it+1} → REHEAT #{n_reheats} "
#                       f"T={reheat_T:.1f}  best={best_r}")

#         c = random.choices(
#             courses_list,
#             weights=[theory_weighted_degree.get(x, 1) for x in courses_list]
#         )[0]
#         sess   = get_sessions(c)
#         m_opts = MORNING_BY_SESSIONS.get(sess, [])
#         e_opts = EVENING_BY_SESSIONS.get(sess, [])
#         if not m_opts or not e_opts: continue

#         r = random.random()
#         old_m, old_e = current[c]
#         if r < 0.40:   new_m, new_e = random.choice(m_opts), old_e
#         elif r < 0.80: new_m, new_e = old_m, random.choice(e_opts)
#         else:          new_m, new_e = random.choice(m_opts), random.choice(e_opts)
#         if new_m == old_m and new_e == old_e: continue

#         delta, affected = delta_move_theory(current, c, new_m, new_e, unsolvable)
#         if delta < 0 or random.random() < math.exp(-delta / T):
#             current[c] = (new_m, new_e)
#             for sid in affected:
#                 courses  = [cc for cc in student_theory_courses[sid] if cc in current]
#                 n        = len(courses)
#                 opts     = [(current[cc][0], current[cc][1]) for cc in courses]
#                 solvable = False
#                 for combo in product(*[[0, 1]] * n):
#                     slots    = [opts[i][combo[i]] for i in range(n)]
#                     conflict = any(sc(slots[i], slots[j])
#                                    for i in range(n) for j in range(i+1, n))
#                     if not conflict: solvable = True; break
#                 if solvable: unsolvable.discard(sid)
#                 else:        unsolvable.add(sid)
#             real = len(unsolvable)
#             if real < best_r:
#                 best_r         = real
#                 best_a         = dict(current)
#                 last_best_iter = it
#                 if best_r == 0:  # ← early stop
#                     print(f"    [{tag}] iter {it+1} → OPTIMAL (0 unsolvable) — stopping early")
#                     return best_a, best_r

#         if (it + 1) % 1000 == 0:
#             print(f"    [{tag}] iter {it+1:6d} | T={T:7.3f} | "
#                   f"unsolvable={len(unsolvable)} best={best_r} | "
#                   f"reheats={n_reheats} | {time.time()-t0:.1f}s")

#     return best_a, best_r

# # ══════════════════════════════════════════════════════════════════
# # LAB SA COMPONENTS
# # ══════════════════════════════════════════════════════════════════

# def build_lab_unsolvable_cache(t_asgn, l_asgn):
#     unsolvable = set()
#     for s in students:
#         sid = s["student_id"]
#         if not student_lab_courses[sid]: continue
#         if not student_has_conflict_free_option(sid, t_asgn, l_asgn):
#             unsolvable.add(sid)
#     return unsolvable

# def delta_move_lab(t_asgn, l_asgn, lab_code, new_m, new_e, unsolvable_set):
#     old_m, old_e = l_asgn[lab_code]
#     if new_m == old_m and new_e == old_e:
#         return 0, set()
#     affected = set(s["student_id"] for s in students
#                    if lab_code in student_lab_courses[s["student_id"]])
#     l_asgn[lab_code] = (new_m, new_e)
#     gained = lost = 0
#     for sid in affected:
#         solvable = student_has_conflict_free_option(sid, t_asgn, l_asgn)
#         was_unsolvable = sid in unsolvable_set
#         if was_unsolvable and solvable:     gained += 1
#         elif not was_unsolvable and not solvable: lost += 1
#     l_asgn[lab_code] = (old_m, old_e)
#     return lost - gained, affected

# def random_lab_assign(t_asgn):
#     l_asgn = {}
#     for lab_code in lab_courses:
#         theory_code = lab_to_theory.get(lab_code)
#         if theory_code not in t_asgn: continue
#         p      = get_lab_p(lab_code)
#         tm, te = t_asgn[theory_code]
#         m_valid = [b for b in LAB_MORNING_BY_P.get(p, []) if not tl_conflict(tm, b)]
#         e_valid = [b for b in LAB_EVENING_BY_P.get(p, []) if not tl_conflict(te, b)]
#         if not m_valid: m_valid = LAB_MORNING_BY_P.get(p, [])
#         if not e_valid: e_valid = LAB_EVENING_BY_P.get(p, [])
#         if m_valid and e_valid:
#             l_asgn[lab_code] = (random.choice(m_valid), random.choice(e_valid))
#     return l_asgn

# # ══════════════════════════════════════════════════════════════════
# # LAB SA RUNNER
# # ══════════════════════════════════════════════════════════════════

# def run_lab_sa(t_asgn, start_l_asgn, iterations, T_start, T_end,
#                tag="LSA", reheat_thresh=6000, reheat_T_frac=0.25):
#     current        = dict(start_l_asgn)
#     unsolvable     = build_lab_unsolvable_cache(t_asgn, current)
#     best_r         = len(unsolvable)
#     best_a         = dict(current)
#     temps          = geometric_schedule(T_start, T_end, iterations)
#     n_reheats      = 0
#     last_best_iter = 0
#     t0             = time.time()
#     lab_list       = list(current.keys())

#     for it in range(iterations):
#         T = temps[it]
#         if it - last_best_iter >= reheat_thresh and T < 1.0 and n_reheats < 5:
#             reheat_T  = reheat_T_frac * T_start
#             remaining = iterations - it
#             if remaining > 1:
#                 temps[it:] = geometric_schedule(reheat_T, T_end, remaining)
#                 T = temps[it]
#                 n_reheats     += 1
#                 last_best_iter = it
#                 print(f"    [{tag}] iter {it+1} → REHEAT #{n_reheats} "
#                       f"T={reheat_T:.1f}  best={best_r}")

#         lab_code = random.choices(
#             lab_list,
#             weights=[lab_enrollment.get(x, 1) for x in lab_list]
#         )[0]
#         theory_code = lab_to_theory.get(lab_code)
#         if theory_code not in t_asgn: continue
#         p      = get_lab_p(lab_code)
#         tm, te = t_asgn[theory_code]
#         m_valid = [b for b in LAB_MORNING_BY_P.get(p, []) if not tl_conflict(tm, b)]
#         e_valid = [b for b in LAB_EVENING_BY_P.get(p, []) if not tl_conflict(te, b)]
#         if not m_valid or not e_valid: continue

#         old_m, old_e = current[lab_code]
#         r = random.random()
#         if r < 0.40:
#             new_m = random.choice(m_valid)
#             new_e = old_e if old_e in e_valid else random.choice(e_valid)
#         elif r < 0.80:
#             new_m = old_m if old_m in m_valid else random.choice(m_valid)
#             new_e = random.choice(e_valid)
#         else:
#             new_m = random.choice(m_valid)
#             new_e = random.choice(e_valid)
#         if new_m == old_m and new_e == old_e: continue

#         delta, affected = delta_move_lab(t_asgn, current, lab_code,
#                                          new_m, new_e, unsolvable)
#         if delta < 0 or random.random() < math.exp(-delta / T):
#             current[lab_code] = (new_m, new_e)
#             for sid in affected:
#                 solvable = student_has_conflict_free_option(sid, t_asgn, current)
#                 if solvable: unsolvable.discard(sid)
#                 else:        unsolvable.add(sid)
#             real = len(unsolvable)
#             if real < best_r:
#                 best_r         = real
#                 best_a         = dict(current)
#                 last_best_iter = it
#                 if best_r == 0:  # ← early stop
#                     print(f"    [{tag}] iter {it+1} → OPTIMAL (0 unsolvable) — stopping early")
#                     return best_a, best_r

#         if (it + 1) % 500 == 0:
#             print(f"    [{tag}] iter {it+1:6d} | T={T:7.3f} | "
#                   f"unsolvable={len(unsolvable)} best={best_r} | "
#                   f"reheats={n_reheats} | {time.time()-t0:.1f}s")

#     return best_a, best_r

# # ══════════════════════════════════════════════════════════════════
# # PHASE 1 — RANDOM INIT + THEORY SA
# # ══════════════════════════════════════════════════════════════════

# print("=" * 65)
# print("  PHASE 1 — Theory SA")
# print("=" * 65)

# def random_theory_assign():
#     asgn = {}
#     for code in theory_courses:
#         sess   = get_sessions(code)
#         m_opts = MORNING_BY_SESSIONS.get(sess, [])
#         e_opts = EVENING_BY_SESSIONS.get(sess, [])
#         if m_opts and e_opts:
#             asgn[code] = (random.choice(m_opts), random.choice(e_opts))
#     return asgn

# asgn          = random_theory_assign()
# p1_u          = len(build_theory_unsolvable_cache(asgn))
# print(f"[P1] Theory courses assigned : {len(asgn)}")
# print(f"[P1] Initial unsolvable      : {p1_u}/{N_STUDENTS}\n")

# T_START    = 200.0
# T_END      = 0.01
# ITERS      = 10_000
# N_RESTARTS = 4

# best_t       = dict(asgn)
# best_t_score = p1_u

# for restart in range(N_RESTARTS):
#     print(f"\n  [R{restart+1}] Theory restart {restart+1}/{N_RESTARTS} ...")
#     if restart == 0:
#         start = dict(best_t)
#     else:
#         start = dict(best_t)
#         frac  = [0.15, 0.25, 0.35][restart % 3]
#         n_p   = max(1, int(len(start) * frac))
#         for c in random.sample(list(start.keys()), n_p):
#             sess   = get_sessions(c)
#             m_opts = MORNING_BY_SESSIONS.get(sess, [])
#             e_opts = EVENING_BY_SESSIONS.get(sess, [])
#             if m_opts and e_opts:
#                 start[c] = (random.choice(m_opts), random.choice(e_opts))
#         pu = len(build_theory_unsolvable_cache(start))
#         print(f"  [R{restart+1}] Perturbed ({frac:.0%}): {pu} unsolvable")

#     ra, rs = run_theory_sa(start, ITERS, T_START, T_END,
#                            tag=f"R{restart+1}",
#                            reheat_thresh=6000, reheat_T_frac=0.25)
#     if rs < best_t_score:
#         best_t_score = rs
#         best_t       = dict(ra)
#     print(f"  [R{restart+1}] unsolvable={rs}  global_best={best_t_score}")

#     if best_t_score == 0:  # ← early stop across restarts
#         print("  [P1] Optimal reached — skipping remaining restarts")
#         break

# final_t    = best_t
# final_t_cf = (N_STUDENTS - best_t_score) / N_STUDENTS * 100
# print(f"\n[P1 FINAL] Theory unsolvable: {best_t_score}/{N_STUDENTS} "
#       f"({final_t_cf:.1f}% solvable)")

# # ══════════════════════════════════════════════════════════════════
# # PHASE 2 — LAB SA
# # ══════════════════════════════════════════════════════════════════

# print("\n" + "=" * 65)
# print("  PHASE 2 — Lab SA (theory fixed)")
# print("=" * 65)

# LAB_T_START    = 100.0
# LAB_T_END      = 0.01
# LAB_ITERS      = 5_000
# LAB_N_RESTARTS = 4

# init_l        = random_lab_assign(final_t)
# init_l_u      = len(build_lab_unsolvable_cache(final_t, init_l))
# print(f"[P2] Lab courses assigned    : {len(init_l)}")
# print(f"[P2] Initial unsolvable      : {init_l_u}/{N_STUDENTS}\n")

# best_l       = dict(init_l)
# best_l_score = init_l_u

# for restart in range(LAB_N_RESTARTS):
#     print(f"\n  [LR{restart+1}] Lab restart {restart+1}/{LAB_N_RESTARTS} ...")
#     if restart == 0:
#         start_l = dict(best_l)
#     else:
#         start_l = dict(best_l)
#         frac    = [0.20, 0.40, 0.60][restart % 3]
#         n_p     = max(1, int(len(start_l) * frac))
#         for lc in random.sample(list(start_l.keys()), n_p):
#             tc     = lab_to_theory.get(lc)
#             p      = get_lab_p(lc)
#             tm, te = final_t[tc]
#             mv     = [b for b in LAB_MORNING_BY_P.get(p, []) if not tl_conflict(tm, b)]
#             ev     = [b for b in LAB_EVENING_BY_P.get(p, []) if not tl_conflict(te, b)]
#             if mv and ev:
#                 start_l[lc] = (random.choice(mv), random.choice(ev))
#         pu = len(build_lab_unsolvable_cache(final_t, start_l))
#         print(f"  [LR{restart+1}] Perturbed ({frac:.0%}): {pu} unsolvable")

#     ra, rs = run_lab_sa(final_t, start_l, LAB_ITERS, LAB_T_START, LAB_T_END,
#                         tag=f"LR{restart+1}",
#                         reheat_thresh=4000, reheat_T_frac=0.30)
#     if rs < best_l_score:
#         best_l_score = rs
#         best_l       = dict(ra)
#     print(f"  [LR{restart+1}] unsolvable={rs}  global_best={best_l_score}")

#     if best_l_score == 0:  # ← early stop across restarts
#         print("  [P2] Optimal reached — skipping remaining restarts")
#         break

# final_l    = best_l
# final_l_cf = (N_STUDENTS - best_l_score) / N_STUDENTS * 100
# print(f"\n[P2 FINAL] Lab unsolvable: {best_l_score}/{N_STUDENTS} "
#       f"({final_l_cf:.1f}% solvable)")

# self_overlaps = sum(
#     1
#     for lab_code, (lm, le) in final_l.items()
#     for tm, te in [final_t.get(lab_to_theory.get(lab_code), (None, None))]
#     if tm and (tl_conflict(tm, lm) or tl_conflict(te, le))
# )
# print(f"[P2] Self T-L overlaps (must be 0): {self_overlaps}")

# # ══════════════════════════════════════════════════════════════════
# # FULL CONFLICT CHECK
# # ══════════════════════════════════════════════════════════════════

# print("\n[Full Check] Verifying unsolvable students (theory + labs)...")
# full_unsolvable = sum(
#     1 for s in students
#     if not student_has_conflict_free_option(s["student_id"], final_t, final_l)
# )
# full_cf = (N_STUDENTS - full_unsolvable) / N_STUDENTS * 100
# print(f"[Full Check] Unsolvable: {full_unsolvable}/{N_STUDENTS} ({full_cf:.1f}% solvable)")

# # ══════════════════════════════════════════════════════════════════
# # PHASE 3 — PER-STUDENT OPTIMAL SECTION ASSIGNMENT
# # ══════════════════════════════════════════════════════════════════

# print("\n[Phase 3] Computing optimal section assignments per student...")

# def best_section_for_student(sid, t_asgn, l_asgn):
#     tcourses = [c for c in student_theory_courses[sid] if c in t_asgn]
#     lcourses = [c for c in student_lab_courses[sid]    if c in l_asgn]
#     nt, nl   = len(tcourses), len(lcourses)
#     if nt + nl == 0:
#         return {}, 0, "pure_morning"

#     t_opts = [(t_asgn[c][0], t_asgn[c][1]) for c in tcourses]
#     l_opts = [(l_asgn[c][0], l_asgn[c][1]) for c in lcourses]

#     def eval_combo(combo):

#         EXAM_PENALTY = 0.1
#         def base_family(slot):
#             return slot.split("+")[0][0]

#         t_combo = combo[:nt]; l_combo = combo[nt:]
#         t_slots = [t_opts[i][t_combo[i]] for i in range(nt)]
#         l_slots = [l_opts[i][l_combo[i]] for i in range(nl)]
#         clashes = 0
#         for i in range(nt):
#             for j in range(i+1, nt):
#                 if tt_conflict(t_slots[i], t_slots[j]): clashes += 1
#         for i in range(nl):
#             for j in range(i+1, nl):
#                 if ll_conflict(l_slots[i], l_slots[j]): clashes += 1
#         for ti, ts in enumerate(t_slots):
#             for li, ls in enumerate(l_slots):
#                 if lab_to_theory.get(lcourses[li]) == tcourses[ti]: continue
#                 if tl_conflict(ts, ls): clashes += 1
#         for ti, tc in enumerate(tcourses):
#             lab_code = theory_to_lab.get(tc)
#             if lab_code and lab_code in lcourses:
#                 li = lcourses.index(lab_code)
#                 if tl_conflict(t_slots[ti], l_slots[li]): clashes += 1
        
#         for i in range(nt):
#             for j in range(i+1, nt):
#                 if base_family(t_slots[i]) == base_family(t_slots[j]):
#                     clashes += EXAM_PENALTY

#         return clashes

#     PURE_MORNING = tuple([0] * nt)
#     PURE_EVENING = tuple([1] * nt)
#     best_clashes = float("inf")
#     best_combo   = None

#     # Pass 1: pure morning theory
#     for l_combo in product(*[[0, 1]] * nl):
#         combo   = PURE_MORNING + l_combo
#         clashes = eval_combo(combo)
#         if clashes < best_clashes:
#             best_clashes = clashes
#             best_combo   = combo
#         if best_clashes == 0: break

#     # Pass 2: pure evening theory
#     if best_clashes > 0:
#         for l_combo in product(*[[0, 1]] * nl):
#             combo   = PURE_EVENING + l_combo
#             clashes = eval_combo(combo)
#             if clashes < best_clashes:
#                 best_clashes = clashes
#                 best_combo   = combo
#             if best_clashes == 0: break

#     # Pass 3: mixed fallback
#     if best_clashes > 0:
#         for combo in product(*[[0, 1]] * (nt + nl)):
#             t_part = combo[:nt]
#             if t_part == PURE_MORNING or t_part == PURE_EVENING: continue
#             clashes = eval_combo(combo)
#             if clashes < best_clashes:
#                 best_clashes = clashes
#                 best_combo   = combo
#             if best_clashes == 0: break

#     t_part = best_combo[:nt]
#     if   t_part == PURE_MORNING: section_type = "pure_morning"
#     elif t_part == PURE_EVENING: section_type = "pure_evening"
#     else:                        section_type = "mixed"

#     result  = {}
#     l_combo = best_combo[nt:]
#     for i, c in enumerate(tcourses):
#         result[c] = {
#             "type":    "theory",
#             "section": "morning" if t_part[i] == 0 else "evening",
#             "slot":    t_opts[i][t_part[i]]
#         }
#     for i, c in enumerate(lcourses):
#         result[c] = {
#             "type":    "lab",
#             "section": "morning" if l_combo[i] == 0 else "evening",
#             "slot":    l_opts[i][l_combo[i]]
#         }
#     return result, best_clashes, section_type

# student_results = {}
# for s in students:
#     sid                   = s["student_id"]
#     combo, clashes, stype = best_section_for_student(sid, final_t, final_l)
#     student_results[sid]  = {
#         "name":         s["name"],
#         "clashes":      clashes,
#         "section_type": stype,
#         "selection":    combo,
#         "solvable":     clashes == 0
#     }

# n_solvable     = sum(1 for v in student_results.values() if v["solvable"])
# n_pure_morning = sum(1 for v in student_results.values() if v["section_type"] == "pure_morning")
# n_pure_evening = sum(1 for v in student_results.values() if v["section_type"] == "pure_evening")
# n_mixed        = sum(1 for v in student_results.values() if v["section_type"] == "mixed")

# print(f"[Phase 3] Zero-conflict students : {n_solvable}/{N_STUDENTS}")
# print(f"[Phase 3] Pure morning           : {n_pure_morning}")
# print(f"[Phase 3] Pure evening           : {n_pure_evening}")
# print(f"[Phase 3] Mixed (fallback)       : {n_mixed}")

# # ══════════════════════════════════════════════════════════════════
# # SAVE OUTPUT
# # ══════════════════════════════════════════════════════════════════

# output = {
#     "timetable": {
#         c: {"morning": m, "evening": e}
#         for c, (m, e) in final_t.items()
#     },
#     "lab_timetable": {
#         c: {"morning": m, "evening": e}
#         for c, (m, e) in final_l.items()
#     },
#     "metrics": {
#         "total_theory_courses":   len(final_t),
#         "total_lab_courses":      len(final_l),
#         "total_students":         N_STUDENTS,
#         "theory_only_unsolvable": best_t_score,
#         "lab_sa_unsolvable":      best_l_score,
#         "full_unsolvable":        full_unsolvable,
#         "solvable_students":      N_STUDENTS - full_unsolvable,
#         "solvable_pct":           round(full_cf, 2),
#         "residual_self_overlaps": self_overlaps,
#         "section_distribution": {
#             "pure_morning": n_pure_morning,
#             "pure_evening": n_pure_evening,
#             "mixed":        n_mixed,
#         }
#     },
#     "student_sections": {
#         sid: {
#             "name":         v["name"],
#             "clashes":      v["clashes"],
#             "solvable":     v["solvable"],
#             "section_type": v["section_type"],
#             "selection": {
#                 c: {
#                     "type":    info["type"],
#                     "section": info["section"],
#                     "slot":    info["slot"]
#                 }
#                 for c, info in v["selection"].items()
#             }
#         }
#         for sid, v in student_results.items()
#     }
# }

# with open("data/two_section_timetable.json", "w") as f:
#     json.dump(output, f, indent=2)

# print("\n[DONE] Saved → data/two_section_timetable.json")
# print(f"       Theory : {len(final_t)} courses  |  unsolvable: {best_t_score}/{N_STUDENTS}")
# print(f"       Lab    : {len(final_l)} courses  |  unsolvable: {best_l_score}/{N_STUDENTS}")
# print(f"       Full   :                    unsolvable: {full_unsolvable}/{N_STUDENTS} ({full_cf:.1f}%)")
# print(f"       Sections: morning={n_pure_morning} | evening={n_pure_evening} | mixed={n_mixed}")






"""
FFCS VIT Chennai — Two-Section SA (Theory + Lab, Two-Phase)
============================================================
Phase 1 : SA optimises theory slot assignment only (fast).
Phase 2 : SA optimises lab slot assignment with theory slots FIXED.
Phase 3 : Per-student optimal section assignment
          (pure morning preferred, pure evening second, mixed fallback).
          Exam-day clashes minimised as secondary objective within Phase 3.

Early stopping: if unsolvable == 0 at any point, halt immediately.
"""

import json, math, random, time
from collections import defaultdict
from itertools import combinations, product

random.seed(42)

# ══════════════════════════════════════════════════════════════════
# SLOT DATA
# ══════════════════════════════════════════════════════════════════

THEORY_PERIOD_TIMES = {
    1:(480,530),  2:(535,585),  3:(590,640),  4:(705,750),
    5:(755,805),  6:(840,890),  7:(895,945),  8:(950,1000),
    9:(1005,1055),10:(1060,1110),11:(1115,1165)
}

SLOT_BUNDLES = {
    "A1":[("MON",1),("WED",2)],  "B1":[("TUE",1),("THU",2)],
    "C1":[("WED",1),("FRI",2)],  "D1":[("THU",1),("MON",3)],
    "E1":[("FRI",1),("TUE",3)],  "F1":[("MON",2),("WED",3)],
    "G1":[("TUE",2),("THU",3)],
    "A2":[("MON",6),("WED",7)],  "B2":[("TUE",6),("THU",7)],
    "C2":[("WED",6),("FRI",7)],  "D2":[("THU",6),("MON",8)],
    "E2":[("FRI",6),("TUE",8)],  "F2":[("MON",7),("WED",8)],
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

MORNING_BUNDLES = {k: v for k, v in SLOT_BUNDLES.items() if "1" in k.split("+")[0][-1]}
EVENING_BUNDLES = {k: v for k, v in SLOT_BUNDLES.items() if "2" in k.split("+")[0][-1]}

VALID_BUNDLES_BY_SESSIONS = {
    2: ["A1","B1","C1","D1","E1","F1","G1",
        "A2","B2","C2","D2","E2","F2","G2"],
    3: ["A1+TA1","B1+TB1","C1+TC1","D1+TD1","E1+TE1","F1+TF1","G1+TG1",
        "A2+TA2","B2+TB2","C2+TC2","D2+TD2","E2+TE2","F2+TF2","G2+TG2"],
    4: ["A1+TA1+TAA1","B1+TB1+TBB1","C1+TC1+TCC1","D1+TD1+TDD1",
        "A2+TA2+TAA2","B2+TB2+TBB2","C2+TC2+TCC2","D2+TD2+TDD2"],
}

MORNING_BY_SESSIONS = {
    sess: [b for b in bundles if b in MORNING_BUNDLES]
    for sess, bundles in VALID_BUNDLES_BY_SESSIONS.items()
}
EVENING_BY_SESSIONS = {
    sess: [b for b in bundles if b in EVENING_BUNDLES]
    for sess, bundles in VALID_BUNDLES_BY_SESSIONS.items()
}

# ══════════════════════════════════════════════════════════════════
# LAB SLOT DATA
# ══════════════════════════════════════════════════════════════════

LAB_SLOT_MAP = {
    "L1":("MON",1),  "L2":("MON",1),
    "L3":("MON",2),  "L4":("MON",2),
    "L5":("MON",3),  "L6":("MON",3),
    "L7":("TUE",1),  "L8":("TUE",1),
    "L9":("TUE",2),  "L10":("TUE",2),
    "L11":("TUE",3), "L12":("TUE",3),
    "L13":("WED",1), "L14":("WED",1),
    "L15":("WED",2), "L16":("WED",2),
    "L19":("THU",1), "L20":("THU",1),
    "L21":("THU",2), "L22":("THU",2),
    "L23":("THU",3), "L24":("THU",3),
    "L25":("FRI",1), "L26":("FRI",1),
    "L27":("FRI",2), "L28":("FRI",2),
    "L29":("FRI",3), "L30":("FRI",3),
    "L31":("MON",6), "L32":("MON",6),
    "L33":("MON",7), "L34":("MON",7),
    "L35":("MON",8), "L36":("MON",8),
    "L37":("TUE",6), "L38":("TUE",6),
    "L39":("TUE",7), "L40":("TUE",7),
    "L41":("TUE",8), "L42":("TUE",8),
    "L43":("WED",6), "L44":("WED",6),
    "L45":("WED",7), "L46":("WED",7),
    "L47":("WED",8), "L48":("WED",8),
    "L49":("THU",6), "L50":("THU",6),
    "L51":("THU",7), "L52":("THU",7),
    "L53":("THU",8), "L54":("THU",8),
    "L55":("FRI",6), "L56":("FRI",6),
    "L57":("FRI",7), "L58":("FRI",7),
    "L59":("FRI",8), "L60":("FRI",8),
}

def _build_lab_pairs():
    all_slots = sorted(LAB_SLOT_MAP.keys(), key=lambda x: int(x[1:]))
    morning_pairs, evening_pairs = [], []
    i = 0
    while i < len(all_slots) - 1:
        s1, s2 = all_slots[i], all_slots[i+1]
        n1, n2 = int(s1[1:]), int(s2[1:])
        if n2 == n1 + 1 and LAB_SLOT_MAP[s1] == LAB_SLOT_MAP[s2]:
            pair = f"{s1}+{s2}"
            (morning_pairs if n1 <= 30 else evening_pairs).append(pair)
            i += 2
        else:
            i += 1
    return morning_pairs, evening_pairs

MORNING_LAB_PAIRS, EVENING_LAB_PAIRS = _build_lab_pairs()

def _build_p4_bundles(pairs):
    bundles = []
    for p1, p2 in combinations(pairs, 2):
        d1 = LAB_SLOT_MAP[p1.split("+")[0]][0]
        d2 = LAB_SLOT_MAP[p2.split("+")[0]][0]
        if d1 != d2:
            n1 = int(p1.split("+")[0][1:])
            n2 = int(p2.split("+")[0][1:])
            bundles.append(f"{p1}+{p2}" if n1 < n2 else f"{p2}+{p1}")
    return bundles

MORNING_P4_BUNDLES = _build_p4_bundles(MORNING_LAB_PAIRS)
EVENING_P4_BUNDLES = _build_p4_bundles(EVENING_LAB_PAIRS)

LAB_MORNING_BY_P = {2: MORNING_LAB_PAIRS, 4: MORNING_P4_BUNDLES}
LAB_EVENING_BY_P = {2: EVENING_LAB_PAIRS, 4: EVENING_P4_BUNDLES}

print(f"P=2 morning lab pairs  : {len(MORNING_LAB_PAIRS)}")
print(f"P=2 evening lab pairs  : {len(EVENING_LAB_PAIRS)}")
print(f"P=4 morning lab bundles: {len(MORNING_P4_BUNDLES)}")
print(f"P=4 evening lab bundles: {len(EVENING_P4_BUNDLES)}")

# ══════════════════════════════════════════════════════════════════
# OVERLAP PRECOMPUTATION
# ══════════════════════════════════════════════════════════════════

def _theory_windows(name):
    return [(d, *THEORY_PERIOD_TIMES[p]) for d, p in SLOT_BUNDLES[name]]

def _lab_windows(bundle_str):
    windows = []
    for slot in bundle_str.split("+"):
        day, period = LAB_SLOT_MAP[slot]
        s, e = THEORY_PERIOD_TIMES[period]
        windows.append((day, s, e))
    return windows

def _windows_overlap(w1, w2):
    for d1, s1, e1 in w1:
        for d2, s2, e2 in w2:
            if d1 == d2 and max(s1, s2) < min(e1, e2):
                return True
    return False

print("\nPrecomputing overlap tables...")

ALL_THEORY_SLOTS   = list(SLOT_BUNDLES.keys())
ALL_THEORY_WINDOWS = {s: _theory_windows(s) for s in ALL_THEORY_SLOTS}
ALL_LAB_BUNDLES    = (MORNING_LAB_PAIRS + EVENING_LAB_PAIRS +
                      MORNING_P4_BUNDLES + EVENING_P4_BUNDLES)
ALL_LAB_WINDOWS    = {b: _lab_windows(b) for b in ALL_LAB_BUNDLES}

TT_OVERLAP = {(a,b): _windows_overlap(ALL_THEORY_WINDOWS[a], ALL_THEORY_WINDOWS[b])
              for a in ALL_THEORY_SLOTS for b in ALL_THEORY_SLOTS}
TL_OVERLAP = {(t,l): _windows_overlap(ALL_THEORY_WINDOWS[t], ALL_LAB_WINDOWS[l])
              for t in ALL_THEORY_SLOTS for l in ALL_LAB_BUNDLES}
LL_OVERLAP = {(a,b): _windows_overlap(ALL_LAB_WINDOWS[a], ALL_LAB_WINDOWS[b])
              for a in ALL_LAB_BUNDLES for b in ALL_LAB_BUNDLES}

sc          = lambda a, b: TT_OVERLAP[(a, b)]
tt_conflict = lambda a, b: TT_OVERLAP[(a, b)]
tl_conflict = lambda t, l: TL_OVERLAP[(t, l)]
ll_conflict = lambda a, b: LL_OVERLAP[(a, b)]

# ── Exam-day base family ───────────────────────────────────────────
# Precompute for all theory slots: "A1+TA1" → "A", "B2" → "B"
SLOT_BASE_FAMILY = {s: s.split("+")[0][0] for s in ALL_THEORY_SLOTS}

def exam_day_pairs(slots):
    """Count same-base-family pairs in a list of assigned theory slots."""
    n = len(slots)
    return sum(
        1 for i in range(n) for j in range(i+1, n)
        if SLOT_BASE_FAMILY[slots[i]] == SLOT_BASE_FAMILY[slots[j]]
    )

EXAM_PENALTY = 0.1  # must be < 1 so exam clash never outweighs a class clash

print("Done.\n")

# ══════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════

with open("data/courses.json") as f: courses_raw = json.load(f)["courses"]
with open("data/recs.json")    as f: students    = json.load(f)["students"]
N_STUDENTS = len(students)

course_map = {c["course_code"]: c for c in courses_raw}

def get_sessions(code):
    c = course_map.get(code)
    return (c.get("L", 0) + c.get("T", 0)) if c else None

def get_lab_p(code):
    c = course_map.get(code)
    return c.get("P", 0) if c else 0

# ══════════════════════════════════════════════════════════════════
# COURSE CLASSIFICATION
# ══════════════════════════════════════════════════════════════════

all_codes = set(c for s in students for c in s["recommended_courses"])

theory_courses = set()
for code in all_codes:
    c = course_map.get(code)
    if c is None: continue
    if c.get("is_lab", False): continue
    if c.get("embedded_lab", False): continue
    sess = get_sessions(code)
    if sess and MORNING_BY_SESSIONS.get(sess) and EVENING_BY_SESSIONS.get(sess):
        theory_courses.add(code)

lab_courses = set()
for code in all_codes:
    c = course_map.get(code)
    if c is None: continue
    if not c.get("is_lab", False): continue
    p = c.get("P", 0)
    if p not in (2, 4): continue
    if not LAB_MORNING_BY_P.get(p) or not LAB_EVENING_BY_P.get(p): continue
    lab_courses.add(code)

lab_to_theory = {}
for code in lab_courses:
    tc = course_map[code].get("theory_course_code")
    if tc:
        lab_to_theory[code] = tc

theory_to_lab = {v: k for k, v in lab_to_theory.items() if k in lab_courses}

print(f"Schedulable theory courses : {len(theory_courses)}")
print(f"Linked lab courses         : {len(lab_courses)}")
print(f"Students                   : {N_STUDENTS}\n")

# ══════════════════════════════════════════════════════════════════
# STUDENT COURSE LISTS
# ══════════════════════════════════════════════════════════════════

student_theory_courses = {}
student_lab_courses    = {}
for s in students:
    sid = s["student_id"]
    student_theory_courses[sid] = [c for c in s["recommended_courses"] if c in theory_courses]
    student_lab_courses[sid]    = [c for c in s["recommended_courses"] if c in lab_courses]

# ══════════════════════════════════════════════════════════════════
# CONFLICT-FREE CHECK
# ══════════════════════════════════════════════════════════════════

def student_has_conflict_free_option(sid, t_asgn, l_asgn):
    tcourses = [c for c in student_theory_courses[sid] if c in t_asgn]
    lcourses = [c for c in student_lab_courses[sid]    if c in l_asgn]
    nt, nl   = len(tcourses), len(lcourses)
    if nt + nl == 0:
        return True
    t_opts = [(t_asgn[c][0], t_asgn[c][1]) for c in tcourses]
    l_opts = [(l_asgn[c][0], l_asgn[c][1]) for c in lcourses]
    for combo in product(*[[0, 1]] * (nt + nl)):
        t_combo = combo[:nt]; l_combo = combo[nt:]
        t_slots = [t_opts[i][t_combo[i]] for i in range(nt)]
        l_slots = [l_opts[i][l_combo[i]] for i in range(nl)]
        conflict = False
        for i in range(nt):
            for j in range(i+1, nt):
                if tt_conflict(t_slots[i], t_slots[j]): conflict = True; break
            if conflict: break
        if not conflict:
            for i in range(nl):
                for j in range(i+1, nl):
                    if ll_conflict(l_slots[i], l_slots[j]): conflict = True; break
                if conflict: break
        if not conflict:
            for ti, ts in enumerate(t_slots):
                for li, ls in enumerate(l_slots):
                    if lab_to_theory.get(lcourses[li]) == tcourses[ti]: continue
                    if tl_conflict(ts, ls): conflict = True; break
                if conflict: break
        if not conflict:
            for ti, tc in enumerate(tcourses):
                lab_code = theory_to_lab.get(tc)
                if lab_code and lab_code in lcourses:
                    li = lcourses.index(lab_code)
                    if tl_conflict(t_slots[ti], l_slots[li]): conflict = True; break
        if not conflict:
            return True
    return False

# ══════════════════════════════════════════════════════════════════
# THEORY SA COMPONENTS
# ══════════════════════════════════════════════════════════════════

def build_theory_unsolvable_cache(asgn):
    unsolvable = set()
    for s in students:
        sid     = s["student_id"]
        courses = [c for c in student_theory_courses[sid] if c in asgn]
        if not courses: continue
        n    = len(courses)
        opts = [(asgn[c][0], asgn[c][1]) for c in courses]
        for combo in product(*[[0, 1]] * n):
            slots    = [opts[i][combo[i]] for i in range(n)]
            conflict = any(sc(slots[i], slots[j])
                           for i in range(n) for j in range(i+1, n))
            if not conflict: break
        else:
            unsolvable.add(sid)
    return unsolvable

def delta_move_theory(asgn, course, new_m, new_e, unsolvable_set):
    old_m, old_e = asgn[course]
    if new_m == old_m and new_e == old_e:
        return 0, set()
    affected = set(s["student_id"] for s in students
                   if course in student_theory_courses[s["student_id"]])
    asgn[course] = (new_m, new_e)
    gained = lost = 0
    for sid in affected:
        courses  = [c for c in student_theory_courses[sid] if c in asgn]
        n        = len(courses)
        opts     = [(asgn[c][0], asgn[c][1]) for c in courses]
        solvable = False
        for combo in product(*[[0, 1]] * n):
            slots    = [opts[i][combo[i]] for i in range(n)]
            conflict = any(sc(slots[i], slots[j])
                           for i in range(n) for j in range(i+1, n))
            if not conflict: solvable = True; break
        was = sid in unsolvable_set
        now = not solvable
        if was and not now: gained += 1
        elif not was and now: lost  += 1
    asgn[course] = (old_m, old_e)
    return lost - gained, affected

adj = defaultdict(dict)
for s in students:
    cs = [c for c in s["recommended_courses"] if c in theory_courses]
    for ca, cb in combinations(cs, 2):
        adj[ca][cb] = adj[ca].get(cb, 0) + 1
        adj[cb][ca] = adj[cb].get(ca, 0) + 1

theory_weighted_degree = {c: sum(adj[c].values()) for c in theory_courses}

lab_enrollment = {
    lc: sum(1 for s in students if lc in student_lab_courses[s["student_id"]])
    for lc in lab_courses
}

def geometric_schedule(T_start, T_end, n):
    if n <= 1: return [T_start]
    f = (T_end / T_start) ** (1.0 / max(n-1, 1))
    return [T_start * (f**i) for i in range(n)]

# ══════════════════════════════════════════════════════════════════
# THEORY SA RUNNER
# ══════════════════════════════════════════════════════════════════

def run_theory_sa(start_asgn, iterations, T_start, T_end,
                  tag="SA", reheat_thresh=8000, reheat_T_frac=0.20):
    current        = dict(start_asgn)
    unsolvable     = build_theory_unsolvable_cache(current)
    best_r         = len(unsolvable)
    best_a         = dict(current)
    temps          = geometric_schedule(T_start, T_end, iterations)
    n_reheats      = 0
    last_best_iter = 0
    t0             = time.time()
    courses_list   = list(current.keys())

    for it in range(iterations):
        T = temps[it]
        if it - last_best_iter >= reheat_thresh and T < 1.0 and n_reheats < 5:
            reheat_T  = reheat_T_frac * T_start
            remaining = iterations - it
            if remaining > 1:
                temps[it:] = geometric_schedule(reheat_T, T_end, remaining)
                T = temps[it]
                n_reheats     += 1
                last_best_iter = it
                print(f"    [{tag}] iter {it+1} → REHEAT #{n_reheats} "
                      f"T={reheat_T:.1f}  best={best_r}")

        c = random.choices(
            courses_list,
            weights=[theory_weighted_degree.get(x, 1) for x in courses_list]
        )[0]
        sess   = get_sessions(c)
        m_opts = MORNING_BY_SESSIONS.get(sess, [])
        e_opts = EVENING_BY_SESSIONS.get(sess, [])
        if not m_opts or not e_opts: continue

        r = random.random()
        old_m, old_e = current[c]
        if r < 0.40:   new_m, new_e = random.choice(m_opts), old_e
        elif r < 0.80: new_m, new_e = old_m, random.choice(e_opts)
        else:          new_m, new_e = random.choice(m_opts), random.choice(e_opts)
        if new_m == old_m and new_e == old_e: continue

        delta, affected = delta_move_theory(current, c, new_m, new_e, unsolvable)
        if delta < 0 or random.random() < math.exp(-delta / T):
            current[c] = (new_m, new_e)
            for sid in affected:
                courses  = [cc for cc in student_theory_courses[sid] if cc in current]
                n        = len(courses)
                opts     = [(current[cc][0], current[cc][1]) for cc in courses]
                solvable = False
                for combo in product(*[[0, 1]] * n):
                    slots    = [opts[i][combo[i]] for i in range(n)]
                    conflict = any(sc(slots[i], slots[j])
                                   for i in range(n) for j in range(i+1, n))
                    if not conflict: solvable = True; break
                if solvable: unsolvable.discard(sid)
                else:        unsolvable.add(sid)
            real = len(unsolvable)
            if real < best_r:
                best_r         = real
                best_a         = dict(current)
                last_best_iter = it
                if best_r == 0:
                    print(f"    [{tag}] iter {it+1} → OPTIMAL (0 unsolvable) — stopping early")
                    return best_a, best_r

        if (it + 1) % 1000 == 0:
            print(f"    [{tag}] iter {it+1:6d} | T={T:7.3f} | "
                  f"unsolvable={len(unsolvable)} best={best_r} | "
                  f"reheats={n_reheats} | {time.time()-t0:.1f}s")

    return best_a, best_r

# ══════════════════════════════════════════════════════════════════
# LAB SA COMPONENTS
# ══════════════════════════════════════════════════════════════════

def build_lab_unsolvable_cache(t_asgn, l_asgn):
    unsolvable = set()
    for s in students:
        sid = s["student_id"]
        if not student_lab_courses[sid]: continue
        if not student_has_conflict_free_option(sid, t_asgn, l_asgn):
            unsolvable.add(sid)
    return unsolvable

def delta_move_lab(t_asgn, l_asgn, lab_code, new_m, new_e, unsolvable_set):
    old_m, old_e = l_asgn[lab_code]
    if new_m == old_m and new_e == old_e:
        return 0, set()
    affected = set(s["student_id"] for s in students
                   if lab_code in student_lab_courses[s["student_id"]])
    l_asgn[lab_code] = (new_m, new_e)
    gained = lost = 0
    for sid in affected:
        solvable = student_has_conflict_free_option(sid, t_asgn, l_asgn)
        was_unsolvable = sid in unsolvable_set
        if was_unsolvable and solvable:          gained += 1
        elif not was_unsolvable and not solvable: lost   += 1
    l_asgn[lab_code] = (old_m, old_e)
    return lost - gained, affected

def random_lab_assign(t_asgn):
    l_asgn = {}
    for lab_code in lab_courses:
        theory_code = lab_to_theory.get(lab_code)
        if theory_code not in t_asgn: continue
        p      = get_lab_p(lab_code)
        tm, te = t_asgn[theory_code]
        m_valid = [b for b in LAB_MORNING_BY_P.get(p, []) if not tl_conflict(tm, b)]
        e_valid = [b for b in LAB_EVENING_BY_P.get(p, []) if not tl_conflict(te, b)]
        if not m_valid: m_valid = LAB_MORNING_BY_P.get(p, [])
        if not e_valid: e_valid = LAB_EVENING_BY_P.get(p, [])
        if m_valid and e_valid:
            l_asgn[lab_code] = (random.choice(m_valid), random.choice(e_valid))
    return l_asgn

# ══════════════════════════════════════════════════════════════════
# LAB SA RUNNER
# ══════════════════════════════════════════════════════════════════

def run_lab_sa(t_asgn, start_l_asgn, iterations, T_start, T_end,
               tag="LSA", reheat_thresh=6000, reheat_T_frac=0.25):
    current        = dict(start_l_asgn)
    unsolvable     = build_lab_unsolvable_cache(t_asgn, current)
    best_r         = len(unsolvable)
    best_a         = dict(current)
    temps          = geometric_schedule(T_start, T_end, iterations)
    n_reheats      = 0
    last_best_iter = 0
    t0             = time.time()
    lab_list       = list(current.keys())

    for it in range(iterations):
        T = temps[it]
        if it - last_best_iter >= reheat_thresh and T < 1.0 and n_reheats < 5:
            reheat_T  = reheat_T_frac * T_start
            remaining = iterations - it
            if remaining > 1:
                temps[it:] = geometric_schedule(reheat_T, T_end, remaining)
                T = temps[it]
                n_reheats     += 1
                last_best_iter = it
                print(f"    [{tag}] iter {it+1} → REHEAT #{n_reheats} "
                      f"T={reheat_T:.1f}  best={best_r}")

        lab_code = random.choices(
            lab_list,
            weights=[lab_enrollment.get(x, 1) for x in lab_list]
        )[0]
        theory_code = lab_to_theory.get(lab_code)
        if theory_code not in t_asgn: continue
        p      = get_lab_p(lab_code)
        tm, te = t_asgn[theory_code]
        m_valid = [b for b in LAB_MORNING_BY_P.get(p, []) if not tl_conflict(tm, b)]
        e_valid = [b for b in LAB_EVENING_BY_P.get(p, []) if not tl_conflict(te, b)]
        if not m_valid or not e_valid: continue

        old_m, old_e = current[lab_code]
        r = random.random()
        if r < 0.40:
            new_m = random.choice(m_valid)
            new_e = old_e if old_e in e_valid else random.choice(e_valid)
        elif r < 0.80:
            new_m = old_m if old_m in m_valid else random.choice(m_valid)
            new_e = random.choice(e_valid)
        else:
            new_m = random.choice(m_valid)
            new_e = random.choice(e_valid)
        if new_m == old_m and new_e == old_e: continue

        delta, affected = delta_move_lab(t_asgn, current, lab_code,
                                         new_m, new_e, unsolvable)
        if delta < 0 or random.random() < math.exp(-delta / T):
            current[lab_code] = (new_m, new_e)
            for sid in affected:
                solvable = student_has_conflict_free_option(sid, t_asgn, current)
                if solvable: unsolvable.discard(sid)
                else:        unsolvable.add(sid)
            real = len(unsolvable)
            if real < best_r:
                best_r         = real
                best_a         = dict(current)
                last_best_iter = it
                if best_r == 0:
                    print(f"    [{tag}] iter {it+1} → OPTIMAL (0 unsolvable) — stopping early")
                    return best_a, best_r

        if (it + 1) % 500 == 0:
            print(f"    [{tag}] iter {it+1:6d} | T={T:7.3f} | "
                  f"unsolvable={len(unsolvable)} best={best_r} | "
                  f"reheats={n_reheats} | {time.time()-t0:.1f}s")

    return best_a, best_r

# ══════════════════════════════════════════════════════════════════
# PHASE 1 — RANDOM INIT + THEORY SA
# ══════════════════════════════════════════════════════════════════

print("=" * 65)
print("  PHASE 1 — Theory SA")
print("=" * 65)

def random_theory_assign():
    asgn = {}
    for code in theory_courses:
        sess   = get_sessions(code)
        m_opts = MORNING_BY_SESSIONS.get(sess, [])
        e_opts = EVENING_BY_SESSIONS.get(sess, [])
        if m_opts and e_opts:
            asgn[code] = (random.choice(m_opts), random.choice(e_opts))
    return asgn

asgn          = random_theory_assign()
p1_u          = len(build_theory_unsolvable_cache(asgn))
print(f"[P1] Theory courses assigned : {len(asgn)}")
print(f"[P1] Initial unsolvable      : {p1_u}/{N_STUDENTS}\n")

T_START    = 200.0
T_END      = 0.01
ITERS      = 10_000
N_RESTARTS = 4

best_t       = dict(asgn)
best_t_score = p1_u

for restart in range(N_RESTARTS):
    print(f"\n  [R{restart+1}] Theory restart {restart+1}/{N_RESTARTS} ...")
    if restart == 0:
        start = dict(best_t)
    else:
        start = dict(best_t)
        frac  = [0.15, 0.25, 0.35][restart % 3]
        n_p   = max(1, int(len(start) * frac))
        for c in random.sample(list(start.keys()), n_p):
            sess   = get_sessions(c)
            m_opts = MORNING_BY_SESSIONS.get(sess, [])
            e_opts = EVENING_BY_SESSIONS.get(sess, [])
            if m_opts and e_opts:
                start[c] = (random.choice(m_opts), random.choice(e_opts))
        pu = len(build_theory_unsolvable_cache(start))
        print(f"  [R{restart+1}] Perturbed ({frac:.0%}): {pu} unsolvable")

    ra, rs = run_theory_sa(start, ITERS, T_START, T_END,
                           tag=f"R{restart+1}",
                           reheat_thresh=6000, reheat_T_frac=0.25)
    if rs < best_t_score:
        best_t_score = rs
        best_t       = dict(ra)
    print(f"  [R{restart+1}] unsolvable={rs}  global_best={best_t_score}")
    if best_t_score == 0:
        print("  [P1] Optimal reached — skipping remaining restarts")
        break

final_t    = best_t
final_t_cf = (N_STUDENTS - best_t_score) / N_STUDENTS * 100
print(f"\n[P1 FINAL] Theory unsolvable: {best_t_score}/{N_STUDENTS} "
      f"({final_t_cf:.1f}% solvable)")

# ══════════════════════════════════════════════════════════════════
# PHASE 2 — LAB SA
# ══════════════════════════════════════════════════════════════════

print("\n" + "=" * 65)
print("  PHASE 2 — Lab SA (theory fixed)")
print("=" * 65)

LAB_T_START    = 100.0
LAB_T_END      = 0.01
LAB_ITERS      = 5_000
LAB_N_RESTARTS = 4

init_l        = random_lab_assign(final_t)
init_l_u      = len(build_lab_unsolvable_cache(final_t, init_l))
print(f"[P2] Lab courses assigned    : {len(init_l)}")
print(f"[P2] Initial unsolvable      : {init_l_u}/{N_STUDENTS}\n")

best_l       = dict(init_l)
best_l_score = init_l_u

for restart in range(LAB_N_RESTARTS):
    print(f"\n  [LR{restart+1}] Lab restart {restart+1}/{LAB_N_RESTARTS} ...")
    if restart == 0:
        start_l = dict(best_l)
    else:
        start_l = dict(best_l)
        frac    = [0.20, 0.40, 0.60][restart % 3]
        n_p     = max(1, int(len(start_l) * frac))
        for lc in random.sample(list(start_l.keys()), n_p):
            tc     = lab_to_theory.get(lc)
            p      = get_lab_p(lc)
            tm, te = final_t[tc]
            mv     = [b for b in LAB_MORNING_BY_P.get(p, []) if not tl_conflict(tm, b)]
            ev     = [b for b in LAB_EVENING_BY_P.get(p, []) if not tl_conflict(te, b)]
            if mv and ev:
                start_l[lc] = (random.choice(mv), random.choice(ev))
        pu = len(build_lab_unsolvable_cache(final_t, start_l))
        print(f"  [LR{restart+1}] Perturbed ({frac:.0%}): {pu} unsolvable")

    ra, rs = run_lab_sa(final_t, start_l, LAB_ITERS, LAB_T_START, LAB_T_END,
                        tag=f"LR{restart+1}",
                        reheat_thresh=4000, reheat_T_frac=0.30)
    if rs < best_l_score:
        best_l_score = rs
        best_l       = dict(ra)
    print(f"  [LR{restart+1}] unsolvable={rs}  global_best={best_l_score}")
    if best_l_score == 0:
        print("  [P2] Optimal reached — skipping remaining restarts")
        break

final_l    = best_l
final_l_cf = (N_STUDENTS - best_l_score) / N_STUDENTS * 100
print(f"\n[P2 FINAL] Lab unsolvable: {best_l_score}/{N_STUDENTS} "
      f"({final_l_cf:.1f}% solvable)")

self_overlaps = sum(
    1
    for lab_code, (lm, le) in final_l.items()
    for tm, te in [final_t.get(lab_to_theory.get(lab_code), (None, None))]
    if tm and (tl_conflict(tm, lm) or tl_conflict(te, le))
)
print(f"[P2] Self T-L overlaps (must be 0): {self_overlaps}")

# ══════════════════════════════════════════════════════════════════
# FULL CONFLICT CHECK
# ══════════════════════════════════════════════════════════════════

print("\n[Full Check] Verifying unsolvable students (theory + labs)...")
full_unsolvable = sum(
    1 for s in students
    if not student_has_conflict_free_option(s["student_id"], final_t, final_l)
)
full_cf = (N_STUDENTS - full_unsolvable) / N_STUDENTS * 100
print(f"[Full Check] Unsolvable: {full_unsolvable}/{N_STUDENTS} ({full_cf:.1f}% solvable)")

# ══════════════════════════════════════════════════════════════════
# PHASE 3 — PER-STUDENT OPTIMAL SECTION ASSIGNMENT
# ══════════════════════════════════════════════════════════════════

print("\n[Phase 3] Computing optimal section assignments per student...")

def best_section_for_student(sid, t_asgn, l_asgn):
    tcourses = [c for c in student_theory_courses[sid] if c in t_asgn]
    lcourses = [c for c in student_lab_courses[sid]    if c in l_asgn]
    nt, nl   = len(tcourses), len(lcourses)
    if nt + nl == 0:
        return {}, 0, 0, "pure_morning"

    t_opts = [(t_asgn[c][0], t_asgn[c][1]) for c in tcourses]
    l_opts = [(l_asgn[c][0], l_asgn[c][1]) for c in lcourses]

    def eval_combo(combo):
        t_combo = combo[:nt]; l_combo = combo[nt:]
        t_slots = [t_opts[i][t_combo[i]] for i in range(nt)]
        l_slots = [l_opts[i][l_combo[i]] for i in range(nl)]

        # ── Class-time clashes (integer) ──────────────────────────
        clashes = 0
        for i in range(nt):
            for j in range(i+1, nt):
                if tt_conflict(t_slots[i], t_slots[j]): clashes += 1
        for i in range(nl):
            for j in range(i+1, nl):
                if ll_conflict(l_slots[i], l_slots[j]): clashes += 1
        for ti, ts in enumerate(t_slots):
            for li, ls in enumerate(l_slots):
                if lab_to_theory.get(lcourses[li]) == tcourses[ti]: continue
                if tl_conflict(ts, ls): clashes += 1
        for ti, tc in enumerate(tcourses):
            lab_code = theory_to_lab.get(tc)
            if lab_code and lab_code in lcourses:
                li = lcourses.index(lab_code)
                if tl_conflict(t_slots[ti], l_slots[li]): clashes += 1

        # ── Exam-day pairs (fractional penalty — never overrides class clash) ──
        exam_pairs = exam_day_pairs(t_slots)

        return clashes + exam_pairs * EXAM_PENALTY, clashes, exam_pairs

    PURE_MORNING = tuple([0] * nt)
    PURE_EVENING = tuple([1] * nt)
    best_score   = float("inf")   # combined score (class + exam penalty)
    best_clashes = float("inf")   # integer class-time clashes
    best_exam    = float("inf")   # integer exam-day pairs
    best_combo   = None

    # Pass 1: pure morning theory
    for l_combo in product(*[[0, 1]] * nl):
        combo              = PURE_MORNING + l_combo
        score, cl, ex      = eval_combo(combo)
        if score < best_score:
            best_score   = score
            best_clashes = cl
            best_exam    = ex
            best_combo   = combo
        if best_clashes == 0 and best_exam == 0: break

    # Pass 2: pure evening theory
    if best_score > 0:
        for l_combo in product(*[[0, 1]] * nl):
            combo         = PURE_EVENING + l_combo
            score, cl, ex = eval_combo(combo)
            if score < best_score:
                best_score   = score
                best_clashes = cl
                best_exam    = ex
                best_combo   = combo
            if best_clashes == 0 and best_exam == 0: break

    # Pass 3: mixed fallback
    if best_score > 0:
        for combo in product(*[[0, 1]] * (nt + nl)):
            t_part = combo[:nt]
            if t_part == PURE_MORNING or t_part == PURE_EVENING: continue
            score, cl, ex = eval_combo(combo)
            if score < best_score:
                best_score   = score
                best_clashes = cl
                best_exam    = ex
                best_combo   = combo
            if best_clashes == 0 and best_exam == 0: break

    t_part = best_combo[:nt]
    if   t_part == PURE_MORNING: section_type = "pure_morning"
    elif t_part == PURE_EVENING: section_type = "pure_evening"
    else:                        section_type = "mixed"

    result  = {}
    l_combo = best_combo[nt:]
    for i, c in enumerate(tcourses):
        result[c] = {
            "type":    "theory",
            "section": "morning" if t_part[i] == 0 else "evening",
            "slot":    t_opts[i][t_part[i]]
        }
    for i, c in enumerate(lcourses):
        result[c] = {
            "type":    "lab",
            "section": "morning" if l_combo[i] == 0 else "evening",
            "slot":    l_opts[i][l_combo[i]]
        }
    return result, best_clashes, best_exam, section_type

student_results = {}
for s in students:
    sid                          = s["student_id"]
    combo, clashes, exam, stype  = best_section_for_student(sid, final_t, final_l)
    student_results[sid] = {
        "name":              s["name"],
        "clashes":           clashes,
        "exam_day_pairs":    exam,
        "section_type":      stype,
        "selection":         combo,
        "solvable":          clashes == 0,
    }

n_solvable          = sum(1 for v in student_results.values() if v["solvable"])
n_pure_morning      = sum(1 for v in student_results.values() if v["section_type"] == "pure_morning")
n_pure_evening      = sum(1 for v in student_results.values() if v["section_type"] == "pure_evening")
n_mixed             = sum(1 for v in student_results.values() if v["section_type"] == "mixed")
n_exam_clash        = sum(1 for v in student_results.values() if v["exam_day_pairs"] > 0)
total_exam_pairs    = sum(v["exam_day_pairs"] for v in student_results.values())
worst_exam_pairs    = max(v["exam_day_pairs"] for v in student_results.values())

print(f"[Phase 3] Zero-conflict students    : {n_solvable}/{N_STUDENTS}")
print(f"[Phase 3] Pure morning              : {n_pure_morning}")
print(f"[Phase 3] Pure evening              : {n_pure_evening}")
print(f"[Phase 3] Mixed (fallback)          : {n_mixed}")
print(f"[Phase 3] Students with exam clashes: {n_exam_clash}/{N_STUDENTS}")
print(f"[Phase 3] Total exam-day pairs      : {total_exam_pairs}")
print(f"[Phase 3] Worst single student      : {worst_exam_pairs} exam-day pair(s)")

# ══════════════════════════════════════════════════════════════════
# SAVE OUTPUT
# ══════════════════════════════════════════════════════════════════

output = {
    "timetable": {
        c: {"morning": m, "evening": e}
        for c, (m, e) in final_t.items()
    },
    "lab_timetable": {
        c: {"morning": m, "evening": e}
        for c, (m, e) in final_l.items()
    },
    "metrics": {
        "total_theory_courses":   len(final_t),
        "total_lab_courses":      len(final_l),
        "total_students":         N_STUDENTS,
        "theory_only_unsolvable": best_t_score,
        "lab_sa_unsolvable":      best_l_score,
        "full_unsolvable":        full_unsolvable,
        "solvable_students":      N_STUDENTS - full_unsolvable,
        "solvable_pct":           round(full_cf, 2),
        "residual_self_overlaps": self_overlaps,
        "section_distribution": {
            "pure_morning": n_pure_morning,
            "pure_evening": n_pure_evening,
            "mixed":        n_mixed,
        },
        "exam_day_metrics": {
            "students_with_exam_clashes": n_exam_clash,
            "total_exam_clash_pairs":     total_exam_pairs,
            "worst_student_pairs":        worst_exam_pairs,
        }
    },
    "student_sections": {
        sid: {
            "name":           v["name"],
            "clashes":        v["clashes"],
            "exam_day_pairs": v["exam_day_pairs"],
            "solvable":       v["solvable"],
            "section_type":   v["section_type"],
            "selection": {
                c: {
                    "type":    info["type"],
                    "section": info["section"],
                    "slot":    info["slot"]
                }
                for c, info in v["selection"].items()
            }
        }
        for sid, v in student_results.items()
    }
}

with open("data/two_section_timetable.json", "w") as f:
    json.dump(output, f, indent=2)

print("\n[DONE] Saved → data/two_section_timetable.json")
print(f"       Theory  : {len(final_t)} courses  |  unsolvable: {best_t_score}/{N_STUDENTS}")
print(f"       Lab     : {len(final_l)} courses  |  unsolvable: {best_l_score}/{N_STUDENTS}")
print(f"       Full    :                    unsolvable: {full_unsolvable}/{N_STUDENTS} ({full_cf:.1f}%)")
print(f"       Sections: morning={n_pure_morning} | evening={n_pure_evening} | mixed={n_mixed}")
print(f"       Exam    : {n_exam_clash} students affected | {total_exam_pairs} total same-day pairs")