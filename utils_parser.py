import fitz
from shared_data import preq, cst_st, arts_st, ss_st, science_st, to_remove, grades, core

# Paste your original classes and functions here exactly as you gave me.
# To avoid redundancy, I'm going to import your entire original code here.
# But since you asked to create util_parser.py, I will just put the relevant functions/classes in this file.

# Copy your full code here (Course_node, Semester_node, extract, add_course, etc.)

class course_node:
    def __init__(self, course, gpa = 0.0 , grade = "F", credit = 3):
        self.course = course
        self.grade = grade
        self.gpa = gpa
        self.credit = credit

    def display(self):
        print(self.course)
        print(self.grade)
        print(self.gpa)
        print(self.credit)

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
            print(course.course, end = " ")
        print()
        print(self.credit)
        print(self.gpa)
        print(self.cgpa)

# Global variables used by functions (to maintain state)
courses_done = {}
semesters_done = {}

def extract(path):
    global courses_done, semesters_done
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
        if lines[i] == "Name" and name == None:
            i += 2
            name = lines[i]
        elif lines[i] == "Student ID" and id == None:
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
                    if lines[i] == "F" or lines[i] == "I" or lines[i] == "W":
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
            credit = 0
            for course in semesters_done[curr_semester].courses:

                if course.course != "CSE400":
                    credit += 3
                else:
                    credit += 4
            semesters_done[curr_semester].credit = credit
        i += 1
    
    semesters_done["NULL"] = semester_node("NULL")
    return name, id, courses_done, semesters_done

def cgpa_upto_null():
    total_points = 0
    total_credits = 0
    
    for course in courses_done:
        node = courses_done[course]
        total_points += node.gpa * node.credit
        total_credits += node.credit
    

    semesters_done["NULL"].cgpa = round(total_points / total_credits, 2) if total_credits else 0.0

def add_course(course, gpa_val):
    semester = "VIRTUAL SEMESTER"  # instead of "NULL"

    credit = 4 if course == "CSE400" else 3

    curr_node = course_node(course, gpa=gpa_val)
    curr_node.credit = credit
    courses_done[course] = curr_node

    if semester not in semesters_done:
        semesters_done[semester] = semester_node(semester)

    semesters_done[semester].courses.append(curr_node)
    semesters_done[semester].credit += credit

    total_points = 0
    total_credits = 0
    for c in semesters_done[semester].courses:
        total_points += c.gpa * c.credit
        total_credits += c.credit

    semesters_done[semester].gpa = round(total_points / total_credits, 2) if total_credits else 0.0

    # Update CGPA field for the virtual semester as well
    total_points_all = 0
    total_credits_all = 0
    for node in courses_done.values():
        total_points_all += node.gpa * node.credit
        total_credits_all += node.credit
    semesters_done[semester].cgpa = round(total_points_all / total_credits_all, 2) if total_credits_all else 0.0
   
def remove_course(course_code):
    semester = "VIRTUAL SEMESTER"

    if course_code not in courses_done:
        return f"{course_code} not found in courses_done."
    if semester not in semesters_done:
        return f"{semester} not initialized."

    course_list = semesters_done[semester].courses
    for i, course in enumerate(course_list):
        if course.course == course_code:
            removed_course = course_list.pop(i)
            semesters_done[semester].credit -= removed_course.credit

            # Recalculate semester GPA
            total_points = sum(c.gpa * c.credit for c in course_list)
            total_credits = sum(c.credit for c in course_list)
            semesters_done[semester].gpa = round(total_points / total_credits, 2) if total_credits else 0.0

            del courses_done[course_code]

            # Recalculate overall CGPA for all semesters
            total_points_all = sum(n.gpa * n.credit for n in courses_done.values())
            total_credits_all = sum(n.credit for n in courses_done.values())
            if total_credits_all:
                semesters_done[semester].cgpa = round(total_points_all / total_credits_all, 2)
            else:
                semesters_done[semester].cgpa = 0.0

            # Remove semester if it's now empty
            if not semesters_done[semester].courses:
                del semesters_done[semester]

            return f"{course_code} removed successfully from {semester}."

    return f"{course_code} not found in {semester}."

def cgpa_projection(target_cgpa=None):
    total_required_credits = 136
    earned_credits = sum(node.credit for node in courses_done.values())
    earned_points = sum(node.gpa * node.credit for node in courses_done.values())

    remaining_credits = max(total_required_credits - earned_credits, 0)
    total_credits = earned_credits + remaining_credits

    max_possible_points = earned_points + (remaining_credits * 4.0)
    max_possible_cgpa = round(max_possible_points / total_credits, 2) if total_credits else 0.0

    result = {"max_cgpa": max_possible_cgpa}

    if target_cgpa is not None:
        required_total_points = target_cgpa * total_credits
        needed_points = required_total_points - earned_points

        if remaining_credits <= 0:
            result["message"] = "All credits completed. Cannot improve CGPA further."
        elif max_possible_cgpa < target_cgpa:
            result["message"] = f"Target CGPA of {target_cgpa} is not achievable. Max possible CGPA is {max_possible_cgpa}."
        else:
            required_avg_gpa = round(needed_points / remaining_credits, 2)
            result["required_avg_gpa"] = required_avg_gpa
            result["message"] = f"To reach a CGPA of {target_cgpa}, you need to average {required_avg_gpa} GPA over the remaining {remaining_credits} credits."

    return result


def cgpa_planner(target_cgpa=None, semesters=0, courses_per_sem=0):
    total_credits_done = sum(course.credit for course in courses_done.values())
    quality_points_done = sum(course.gpa * course.credit for course in courses_done.values())

    total_required_credits = 136
    remaining_credits = total_required_credits - total_credits_done

    planned_courses = semesters * courses_per_sem
    max_possible_courses = (remaining_credits + 2) // 3  # rounding up
    planned_courses = min(planned_courses, max_possible_courses)
    planned_credits = min(planned_courses * 3, remaining_credits)

    total_quality_points = quality_points_done + (planned_credits * 4.0)
    total_credits = total_credits_done + planned_credits

    max_possible_cgpa = round(total_quality_points / total_credits, 2) if total_credits else 0.0
    result = {"max_cgpa": max_possible_cgpa}

    if target_cgpa is not None:
        total_required_points = target_cgpa * total_credits
        needed_points = total_required_points - quality_points_done

        if planned_credits <= 0:
            result["message"] = "No valid credits planned. Cannot calculate required GPA."
        else:
            required_avg_gpa = needed_points / planned_credits
            required_avg_gpa = round(required_avg_gpa, 2)

            if required_avg_gpa > 4.0:
                result["required_avg_gpa"] = required_avg_gpa
                result["message"] = f"Target CGPA of {target_cgpa} is not achievable with current plan. Required GPA: {required_avg_gpa}."
            else:
                result["required_avg_gpa"] = required_avg_gpa
                result["message"] = f"To reach CGPA {target_cgpa}, you must average {required_avg_gpa} GPA in the next {planned_courses} courses ({planned_credits} credits)."

    return result

def cod_planner():
    maximum = 5
    cst = 0
    arts = 0
    ss = 0
    science = 0

    taken = set()

    for course in courses_done:
        if course in cst_st:
            cst += 1
            taken.add(course)
        elif course in arts_st:
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
        for course in arts_st:
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

    combined_pool = list(arts_st | ss_st | science_st)
    for course in combined_pool:
        if remaining == 0:
            break
        if course not in taken:
            plan.append(course)
            taken.add(course)
            remaining -= 1

    result["plan"] = plan
    return result

def simulate_retake(regrades):
    total_points = 0
    total_credits = 0

    for course, node in courses_done.items():
        if course in regrades:
            new_gpa = regrades[course]
            total_points += new_gpa * node.credit
        else:
            total_points += node.gpa * node.credit
        total_credits += node.credit

    new_cgpa = round(total_points / total_credits, 2) if total_credits else 0.0

    result = {
        "new_cgpa": new_cgpa,
        "message": f"After retaking specified courses, your projected CGPA would be {new_cgpa}."
    }
    return result

def get_unlocked_courses():
    completed = set(courses_done.keys())
    
    # Build prereq map: course → list of prerequisites
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
