import os
import json
import fitz
from streamlit.runtime.scriptrunner import get_script_run_ctx
from shared_data import preq, cst_st, arts_st, ss_st, science_st, to_remove, grades, core, comp_cod, tarc

class course_node:
    def __init__(self, course, gpa=0.0, grade="F", credit=3):
        self.course = course
        self.grade = grade
        self.gpa = gpa
        self.credit = credit

    def display(self):
        print(self.course, self.grade, self.gpa, self.credit)

class semester_node:
    def __init__(self, semester):
        self.semester = semester
        self.courses = []
        self.credit = 0
        self.gpa = 0
        self.cgpa = 0

    def display(self):
        print(self.semester)
        for course in self.courses:
            print(course.course, end=" ")
        print(self.credit, self.gpa, self.cgpa)

def extract(path):
    courses_done = {}
    semesters_done = {}

    name, id = None, None
    doc = fitz.open(path)
    full_text = ""

    for page in doc:
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        for block in blocks:
            full_text += block[4] + "\n"

    lines = full_text.splitlines()
    i = 0

    for word in lines:
        if word in to_remove:
            lines.remove(word)

    while i < len(lines):
        if lines[i] == "Name" and name is None:
            i += 2
            name = lines[i]
        elif lines[i] == "Student ID" and id is None:
            i += 2
            id = lines[i]
        elif lines[i] == "SEMESTER:":
            i += 1
            curr_semester = lines[i]
            semesters_done[curr_semester] = semester_node(curr_semester)

            while lines[i] != "CGPA":
                if lines[i] in preq:
                    curr_course = lines[i]
                    nt = False
                    while lines[i] not in grades:
                        if "(NT)" in lines[i]:
                            nt = True
                            break
                        elif "(RP)" in lines[i] or "(RT)" in lines[i]:
                            hold = lines[i].split()
                            lines[i] = hold[0]
                            break
                        i += 1

                    if nt:
                        continue
                    if lines[i] in {"F", "I", "W"}:
                        continue

                    courses_done[curr_course] = course_node(curr_course)
                    courses_done[curr_course].credit = float(lines[i - 1])
                    courses_done[curr_course].grade = lines[i]
                    courses_done[curr_course].gpa = float(lines[i + 1])
                    semesters_done[curr_semester].courses.append(courses_done[curr_course])
                elif lines[i] == "SEMESTER":
                    while lines[i] != "Credits Earned":
                        i += 1
                    semesters_done[curr_semester].gpa = float(lines[i + 3])
                i += 1

            semesters_done[curr_semester].cgpa = float(lines[i + 1])
            credit = sum(4 if c.course == "CSE400" else 3 for c in semesters_done[curr_semester].courses)
            semesters_done[curr_semester].credit = credit
        i += 1

    semesters_done["NULL"] = semester_node("NULL")
    return name, id, courses_done, semesters_done

def add_course(course, gpa_val, courses_done, semesters_done):
    semester = "VIRTUAL SEMESTER"
    credit = 4 if course == "CSE400" else 3

    if course in courses_done:
        remove_course(course, courses_done, semesters_done)

    curr_node = course_node(course, gpa=gpa_val)
    curr_node.credit = credit
    courses_done[course] = curr_node

    if semester not in semesters_done:
        semesters_done[semester] = semester_node(semester)

    semesters_done[semester].courses.append(curr_node)
    semesters_done[semester].credit += credit

    total_points = sum(c.gpa * c.credit for c in semesters_done[semester].courses)
    total_credits = sum(c.credit for c in semesters_done[semester].courses)
    semesters_done[semester].gpa = round(total_points / total_credits, 2) if total_credits else 0.0

    total_points_all = sum(n.gpa * n.credit for n in courses_done.values())
    total_credits_all = sum(n.credit for n in courses_done.values())
    semesters_done[semester].cgpa = round(total_points_all / total_credits_all, 2) if total_credits_all else 0.0

def remove_course(course_code, courses_done, semesters_done):
    semester = "VIRTUAL SEMESTER"
    if course_code not in courses_done or semester not in semesters_done:
        return

    course_list = semesters_done[semester].courses
    for i, course in enumerate(course_list):
        if course.course == course_code:
            removed_course = course_list.pop(i)
            semesters_done[semester].credit -= removed_course.credit


            total_points = sum(c.gpa * c.credit for c in course_list)
            total_credits = sum(c.credit for c in course_list)
            semesters_done[semester].gpa = round(total_points / total_credits, 2) if total_credits else 0.0

            del courses_done[course_code]

            total_points_all = sum(n.gpa * n.credit for n in courses_done.values())
            total_credits_all = sum(n.credit for n in courses_done.values())
            semesters_done[semester].cgpa = round(total_points_all / total_credits_all, 2) if total_credits_all else 0.0

            if not semesters_done[semester].courses:
                del semesters_done[semester]
            return

def cgpa_projection(courses_done, target_cgpa=None, total_required_credits=136):
    earned_credits = sum(node.credit for node in courses_done.values())
    earned_points = sum(node.gpa * node.credit for node in courses_done.values())

    remaining_credits = max(total_required_credits - earned_credits, 0)
    total_credits = earned_credits + remaining_credits

    max_possible_points = earned_points + (remaining_credits * 4.0)
    max_possible_cgpa = max_possible_points / total_credits if total_credits else 0.0

    rounded_max_cgpa = round(max_possible_cgpa, 2)
    result = {"max_cgpa": rounded_max_cgpa}

    if target_cgpa is not None:
        target_cgpa = round(target_cgpa, 2)
        required_total_points = target_cgpa * total_credits
        needed_points = required_total_points - earned_points

        if remaining_credits <= 0:
            result["message"] = "All credits completed. Cannot improve CGPA further."
        elif rounded_max_cgpa == target_cgpa:
            result["required_avg_gpa"] = 4.00
            result["message"] = (
                f"To reach a CGPA of {target_cgpa}, you must get 4.00 GPA in all remaining courses."
            )
        elif rounded_max_cgpa < target_cgpa:
            result["message"] = (
                f"Target CGPA of {target_cgpa} is not achievable. "
                f"Max possible CGPA is {rounded_max_cgpa}."
            )
        else:
            required_avg_gpa = (needed_points / remaining_credits)
            rounded_required_gpa = round(required_avg_gpa, 2)
            result["required_avg_gpa"] = rounded_required_gpa
            result["message"] = (
                f"To reach a CGPA of {target_cgpa}, you need to average "
                f"{rounded_required_gpa} GPA over the remaining {remaining_credits} credits."
            )
    return result

def cgpa_planner(courses_done, target_cgpa=None, semesters=0, courses_per_sem=0, total_required_credits=136):
    total_credits_done = sum(course.credit for course in courses_done.values())
    quality_points_done = sum(course.gpa * course.credit for course in courses_done.values())

    remaining_credits = total_required_credits - total_credits_done
    planned_courses = semesters * courses_per_sem

    max_possible_courses = (remaining_credits + 2) // 3
    planned_courses = min(planned_courses, max_possible_courses)
    planned_credits = min(planned_courses * 3, remaining_credits)

    total_quality_points = quality_points_done + (planned_credits * 4.0)
    total_credits = total_credits_done + planned_credits

    raw_max_cgpa = total_quality_points / total_credits if total_credits else 0.0
    max_possible_cgpa = round(raw_max_cgpa, 2)
    result = {"max_cgpa": max_possible_cgpa}

    if target_cgpa is not None:
        target_cgpa = round(target_cgpa, 2)
        total_required_points = target_cgpa * total_credits
        needed_points = total_required_points - quality_points_done

        if planned_credits <= 0:
            result["message"] = "No valid credits planned. Cannot calculate required GPA."
        elif max_possible_cgpa == target_cgpa:
            result["required_avg_gpa"] = 4.00
            result["message"] = (
                f"To reach CGPA {target_cgpa}, you must get 4.00 GPA in all planned courses."
            )
        elif max_possible_cgpa < target_cgpa:
            result["required_avg_gpa"] = round(needed_points / planned_credits, 2)
            result["message"] = (
                f"Target CGPA of {target_cgpa} is not achievable with current plan. "
                f"Required GPA: {result['required_avg_gpa']}."
            )
        else:
            required_avg_gpa = needed_points / planned_credits
            rounded_required_gpa = round(required_avg_gpa, 2)
            result["required_avg_gpa"] = rounded_required_gpa
            result["message"] = (
                f"To reach CGPA {target_cgpa}, you must average "
                f"{rounded_required_gpa} GPA in the next {planned_courses} courses "
                f"({planned_credits} credits)."
            )
    return result

def cod_planner(courses_done):
    from shared_data import cst_st, ss_st, science_st
    from utils_parser import get_session_cod_sets

    comp_cod_session, arts_st_session = get_session_cod_sets(courses_done)

    maximum = 5
    cst = arts = ss = science = 0
    taken = set()

    for course in courses_done:
        if course in cst_st:
            cst += 1
            taken.add(course)
        elif course in arts_st_session:
            arts += 1
            taken.add(course)
        elif course in science_st:
            science += 1
            taken.add(course)
        elif course in ss_st:
            ss += 1
            taken.add(course)

    total_taken = cst + arts + ss + science
    remaining = maximum - total_taken

    result = {
        "total_taken": total_taken,
        "max": maximum,
        "cst": cst,
        "arts": arts,
        "ss": ss,
        "science": science,
        "plan": [],
        "message": ""
    }

    if total_taken >= maximum:
        result["message"] = "You have already completed the maximum number of CODs allowed."
        return result

    plan = []

    if arts == 0:
        for course in arts_st_session:
            if course not in taken:
                plan.append(course)
                taken.add(course)
                remaining -= 1
                break

    if ss == 0 and remaining > 0:
        for course in ss_st:
            if course not in taken:
                plan.append(course)
                taken.add(course)
                remaining -= 1
                break

    if cst == 0 and remaining > 0:
        for course in cst_st:
            if course not in taken:
                plan.append(course)
                taken.add(course)
                remaining -= 1
                break

    if remaining > 0:
        for course in science_st:
            if course not in taken:
                plan.append(course)
                taken.add(course)
                remaining -= 1
                break

    combined_pool = list(arts_st_session | ss_st | science_st)
    for course in combined_pool:
        if remaining == 0:
            break
        if course not in taken:
            plan.append(course)
            taken.add(course)
            remaining -= 1

    result["plan"] = plan
    return result

def simulate_retake(courses_done, regrades):
    total_points = 0
    total_credits = 0

    for course, node in courses_done.items():
        if course in regrades:
            total_points += regrades[course] * node.credit
        else:
            total_points += node.gpa * node.credit
        total_credits += node.credit

    new_cgpa = round(total_points / total_credits, 2) if total_credits else 0.0
    return {
        "new_cgpa": new_cgpa,
        "message": f"After retaking specified courses, your projected CGPA would be {new_cgpa}."
    }

def get_unlocked_courses(courses_done):
    completed = set(courses_done.keys())
    prereq_map = {}
    reverse_unlock_map = {}

    for course, unlocks in preq.items():
        for unlocked_course in unlocks:
            prereq_map.setdefault(unlocked_course, []).append(course)
            reverse_unlock_map.setdefault(course, []).append(unlocked_course)

    unlocked_now = set()
    for course in prereq_map:
        if course in completed:
            continue
        prereqs = prereq_map.get(course, [])
        if all(p in completed for p in prereqs):
            unlocked_now.add(course)

    return unlocked_now, reverse_unlock_map

def get_all_course_codes():
    all_codes = set(preq.keys())
    for lst in preq.values():
        all_codes.update(lst)

    all_codes.update(science_st)
    all_codes.update(arts_st)
    all_codes.update(cst_st)
    all_codes.update(ss_st)
    all_codes.update(comp_cod)
    all_codes.update(core)
    all_codes.update(tarc)

    all_codes.difference_update(to_remove)

    return sorted(all_codes)

def load_course_resources(course_code, resource_dir="resources"):
    filename = course_code.replace("/", "_") + ".json"
    file_path = os.path.join(resource_dir, filename)
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None

def get_session_cod_sets(courses_done):
    comp_cod_session = set(comp_cod)
    arts_st_session = set(arts_st)
    if "ENG101" not in courses_done and "ENG102" in courses_done:
        comp_cod_session.add("ENG103")
        if "ENG103" in arts_st_session:
            arts_st_session.remove("ENG103")
    return comp_cod_session, arts_st_session