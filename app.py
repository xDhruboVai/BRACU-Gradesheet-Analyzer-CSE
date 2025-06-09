import os
import datetime
import random
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils_parser import (
    extract, add_course, remove_course, simulate_retake,
    cgpa_projection, cgpa_planner, cod_planner, course_node,
    get_unlocked_courses, get_all_course_codes, load_course_resources, get_session_cod_sets
)
from shared_data import (
    preq, arts_st, cst_st, core, science_st, ss_st, labs, comp_cod, tarc, cs_elective
)

st.set_page_config(
    page_title="BRACU Gradesheet Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

with open("meta.html") as f:
    st.components.v1.html(f.read(), height=0)

st.markdown('''
<style>
/* Set background */
html, body, .stApp {
    background-color: #000 !important;
    color: white !important;
}

/* Text color */
h1, h2, h3, h4, h5, h6, p, span, div, label, input, textarea {
    color: white !important;
}

/* Highlight color */
strong {
    color: #80DFFF !important;
}

/* Streamlit widgets background */
[data-testid="stSidebar"], [data-testid="stVerticalBlock"], .css-1cpxqw2, .css-ffhzg2 {
    background-color: #000 !important;
    color: white !important;
}
</style>
''', unsafe_allow_html=True)


# Theme and header
st.title("📊 BRACU Gradesheet Analyzer (CSE & CS)")
st.markdown("Analyze your BRAC University Gradesheet, calculate CGPA, visualize trends and plan courses.")

# Session state setup
if "name" not in st.session_state:
    st.session_state.name = ""
    st.session_state.id = ""
    st.session_state.uploaded = False
    st.session_state.retakes = {}
    st.session_state.regrades = {}
    st.session_state.original_gpas = {}
    st.session_state.added_courses = set()
    st.session_state.courses_done = {}
    st.session_state.semesters_done = {}
    st.session_state.dept = "CSE"
    
if "prev_dept" not in st.session_state:
    st.session_state.prev_dept = st.session_state.get("dept", "CSE")


st.sidebar.title("Gradesheet Upload")

# Department selection
st.session_state.dept = st.sidebar.radio(
    label="",
    options=["CSE", "CS"],
    horizontal=True,
    index=0 if st.session_state.get("dept", "CSE") == "CSE" else 1,
    key="dept_selector"
)

# Trigger rerun if selection changed
if st.session_state.dept != st.session_state.get("prev_dept"):
    st.session_state.prev_dept = st.session_state.dept
    st.rerun()


if not st.session_state.uploaded:
    pdf = st.sidebar.file_uploader("Upload your Gradesheet", type="pdf")

    if pdf:
        with open("temp.pdf", "wb") as f:
            f.write(pdf.read())
        name, sid, c_done, s_done = extract("temp.pdf")
        st.session_state.name = name
        st.session_state.id = sid
        st.session_state.uploaded = True
        st.session_state.courses_done = c_done
        st.session_state.semesters_done = s_done
        st.session_state.original_gpas = {c: n.gpa for c, n in c_done.items()}
        st.session_state.info_refreshed = False
        st.rerun()

else:
    st.sidebar.write("✅ Gradesheet uploaded! Refresh the page to upload another.\n\nYou can close this sidebar by pressing the arrow on the **top right**.")



# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Courses & Retake", "CGPA Planner", "COD Planner", "Visual Analytics", "Unlocked Courses", "Course Resources", "Completed Course Breakdown"
])


# Helper: calculate CGPA
def calculate_cgpa():
    courses_done = st.session_state.courses_done
    total_credits = sum(c.credit for c in courses_done.values())
    total_points = sum(c.gpa * c.credit for c in courses_done.values())
    return (round(total_points / total_credits, 2) if total_credits else 0.0, total_credits)

# Helper: refresh info
def refresh_info():
    cgpa, credits = calculate_cgpa()
    st.session_state.cgpa = cgpa
    st.session_state.total_credits = credits

if "cgpa" not in st.session_state:
    refresh_info()

# ========== TAB 1 ==========
with tab1:
    st.header("Student & Academic Info")
    st.markdown(
    """
    <div style="
        border: 1px solid #dcdcdc;
        border-radius: 10px;
        padding: 15px 20px;
        background-color: #00000;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        font-size: 14px;
        line-height: 1.5;
    ">
        <strong>ℹ️ Note: Read this before proceeding</strong><br><br>
        Any change you make here — such as adding, retaking, or removing a course — will <strong>automatically</strong> update:
        <ul style="margin-top: 5px; margin-bottom: 5px;">
            <li>CGPA planner</li>
            <li>CGPA projection</li>
            <li>Visual analytics</li>
            <li>Unlocked courses</li>
            <li>Completed course breakdown</li>
        </ul>
        You can remove added or retaken courses using the <strong>REMOVE COURSE</strong> section below.<br><br>
        <strong>For CS students:</strong> Please check the <strong>CS</strong> option in the sidebar  
        <em>(press the arrow on the top left to open the sidebar)</em>.
    </div>
    """,
    unsafe_allow_html=True
)

    col1, col2, col3 = st.columns([3, 3, 1])
    blur = col1.checkbox("Blur personal info")
    refresh = None

    if refresh:
        refresh_info()
        st.session_state.info_refreshed = True
        st.success("Student info refreshed!")

    if st.session_state.uploaded:
        if not st.session_state.get("info_refreshed", False):
            refresh_info()
            st.session_state.info_refreshed = True
            st.success("Student info refreshed!")

        name = '[Hidden]' if blur else st.session_state.name
        student_id = '[Hidden]' if blur else st.session_state.id

        st.text(f"Name: {name}")
        st.text(f"ID: {student_id}")
        st.metric("Credits Earned", st.session_state.total_credits)
        st.metric("CGPA", st.session_state.cgpa)

        st.markdown("---")
        col_left, col_right = st.columns(2)

        # Add course
        with col_left:
            st.subheader("➕ Add a Course")
            all_course_codes = get_all_course_codes()
            eligible_to_add = [
                code for code in all_course_codes
                if code not in st.session_state.courses_done
                and code not in st.session_state.added_courses
            ]

            new_code = st.selectbox("Select New Course to Add", options=eligible_to_add, key="new_course_select")
            new_gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, step=0.01, key="new_course_gpa")
            can_add = bool(new_code)

            if st.button("Add Course", disabled=not can_add):
                add_course(new_code, new_gpa, st.session_state.courses_done, st.session_state.semesters_done)
                st.session_state.original_gpas[new_code] = new_gpa
                st.session_state.added_courses.add(new_code)
                refresh_info()
                st.session_state.info_refreshed = True
                st.rerun()



        # Retake course
        with col_right:
            st.subheader("🔁 Retake a Course")
            retake_options = [
                code for code, node in st.session_state.courses_done.items()
                if node.gpa < 4.0 and code not in st.session_state.retakes
            ]
            course_to_retake = st.selectbox("Select Course to Retake", retake_options, key="retake_select")
            retake_gpa = st.number_input("New GPA", min_value=0.0, max_value=4.0, step=0.01, key="retake_gpa")

            if st.button("Retake Course", disabled=not course_to_retake):
                st.session_state.retakes[course_to_retake] = retake_gpa
                if course_to_retake not in st.session_state.original_gpas:
                    st.session_state.original_gpas[course_to_retake] = st.session_state.courses_done[course_to_retake].gpa
                add_course(course_to_retake, retake_gpa, st.session_state.courses_done, st.session_state.semesters_done)
                refresh_info()
                st.session_state.info_refreshed = True
                st.rerun()



        st.markdown("---")
        st.subheader("🗑️ Remove a Course")
        removable = list(st.session_state.added_courses.union(st.session_state.retakes.keys()))
        selected_remove = st.multiselect("Select course(s) to remove", options=removable)

        if st.button("Remove Selected Course(s)", disabled=not selected_remove):
            for course in selected_remove:
                if course in st.session_state.retakes:
                    remove_course(course, st.session_state.courses_done, st.session_state.semesters_done)
                    orig_gpa = st.session_state.original_gpas.get(course)
                    if orig_gpa is not None:
                        credit = 4 if course == "CSE400" else 3
                        st.session_state.courses_done[course] = course_node(course, gpa=orig_gpa)
                        st.session_state.courses_done[course].credit = credit
                    st.session_state.retakes.pop(course, None)
                    st.session_state.regrades.pop(course, None)
                elif course in st.session_state.added_courses:
                    st.session_state.added_courses.remove(course)
                    st.session_state.original_gpas.pop(course, None)
                    remove_course(course, st.session_state.courses_done, st.session_state.semesters_done)
            refresh_info()
            st.session_state.info_refreshed = True
            st.rerun()
    else:
        st.info("Upload a Gradesheet to begin.")

# ========== TAB 2 ==========
with tab2:
    st.header("📊 CGPA Planner & Projection")

    st.subheader("🎯 Set Your Target CGPA")
    target_cgpa = st.number_input("Target CGPA", min_value=0.0, max_value=4.0, step=0.01)

    st.markdown("---")

    col1, col2 = st.columns(2)

    # === CGPA Planner ===
    with col1:
        st.subheader("🧮 CGPA Planner")

        with st.form("cgpa_planner_form"):
            st.write("Plan your upcoming semesters:")

            sem_col1, sem_col2 = st.columns(2)
            semesters = sem_col1.number_input("Future Semesters", min_value=0, step=1)
            courses_per_sem = sem_col2.slider("Courses per Semester", min_value=0, max_value=6, value=4)

            submitted = st.form_submit_button("📈 Run CGPA Planner")

        if submitted:
            if semesters == 0 or courses_per_sem == 0:
                st.warning("Please enter both future semesters and courses per semester to plan ahead.")

                # Show current CGPA
                done_courses = st.session_state.courses_done
                total_credits = sum(c.credit for c in done_courses.values())
                total_points = sum(c.gpa * c.credit for c in done_courses.values())
                current_cgpa = round(total_points / total_credits, 2) if total_credits else 0.0
                st.metric("Current CGPA", current_cgpa)
            else:
                required_credits = 136 if st.session_state.dept == "CSE" else 124
                result = cgpa_planner(
                    st.session_state.courses_done,
                    round(target_cgpa, 2),
                    semesters,
                    courses_per_sem,
                    total_required_credits=required_credits
                )
                st.metric("Max Possible CGPA", result.get("max_cgpa", 0.0))
                if "required_avg_gpa" in result:
                    st.metric("Required Avg GPA", result["required_avg_gpa"])
                if "message" in result:
                    st.info(result["message"])

    # === CGPA Projection ===
    with col2:
        st.subheader("🔍 Max CGPA Projection")
        st.write("Estimate your highest achievable CGPA from current progress.")

        if st.button("Run Max CGPA Projection"):
            required_credits = 136 if st.session_state.dept == "CSE" else 124
            proj = cgpa_projection(st.session_state.courses_done, target_cgpa, total_required_credits=required_credits)
            st.metric("Max Achievable CGPA", proj.get("max_cgpa", 0.0))
            if "message" in proj:
                st.info(proj["message"])


# ========== TAB 3 ==========
with tab3:
    st.header("📚 COD Planner")

    from utils_parser import get_session_cod_sets
    comp_cod_session, arts_st_session = get_session_cod_sets(st.session_state.courses_done)

    if st.button("🎯 Generate COD Plan"):
        cod = cod_planner(st.session_state.courses_done)
        taken_courses = set(st.session_state.courses_done.keys())

        st.metric("Total CODs Completed", f"{cod['total_taken']} / 5")

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        col1.metric("Arts", cod["arts"])
        col2.metric("Social Sciences", cod["ss"])
        col3.metric("CST", cod["cst"])
        col4.metric("Science", cod["science"])

        st.markdown("### 💡 Recommended Streams to Prioritize")
        if cod["total_taken"] >= 5:
            st.success("✅ You have completed the maximum number of CODs allowed (5).")
        else:
            recommendations = []
            if cod["arts"] == 0:
                recommendations.append("Arts (Required)")
            if cod["ss"] == 0:
                recommendations.append("Social Sciences (Required)")
            if cod["cst"] == 0:
                recommendations.append("CST (Choose at most one)")
            if cod["science"] == 0:
                recommendations.append("Science (Optional)")

            if recommendations:
                for r in recommendations:
                    st.markdown(f"- {r}")
            else:
                st.info("You’ve met all stream coverage requirements. Pick any remaining CODs to reach 5.")

        st.markdown("### 📚 Remaining COD Courses by Stream")
        stream_map = {
            "Arts": arts_st_session,
            "Social Sciences": ss_st,
            "CST": cst_st,
            "Science": science_st
        }

        for stream_label, course_set in stream_map.items():
            remaining = sorted([c for c in course_set if c not in taken_courses])
            with st.expander(f"{stream_label} ({len(remaining)} remaining)"):
                st.write("• " + "\n• ".join(remaining) if remaining else "✅ All courses in this stream completed.")

# ========== TAB 4 ==========
with tab4:
    st.header("📊 Visual Analytics Dashboard")

    completed = st.session_state.total_credits
    required_credits = 136 if st.session_state.dept == "CSE" else 124
    remaining = required_credits - completed


    fig_pie = go.Figure(data=[go.Pie(
        labels=["Completed", "Remaining"],
        values=[completed, remaining],
        hole=0.3,
        marker=dict(colors=['#00cc96', '#EF553B']),
    )])
    fig_pie.update_traces(textinfo='label+percent')
    fig_pie.update_layout(
        title=f"Credits Earned vs Remaining (out of {required_credits})",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # GPA trend
    st.subheader("📈 GPA & CGPA Trend")
    st.markdown("""
        ***Double-click*** to reset the graph view.  
        **Hover over GPA points** to see which course deviated the most from the average.  
        *Zoom in as much as you like — a quick double-click will always bring you back to sanity.*
        """)

    def semester_sort_key(sem_str):
        if sem_str == "VIRTUAL SEMESTER":
            return (9999, 3)
        semester_order = {"SPRING": 0, "SUMMER": 1, "FALL": 2}
        try:
            sem, year = sem_str.split()
            return (int(year), semester_order.get(sem.upper(), 99))
        except:
            return (9999, 99)

    sem_data = st.session_state.semesters_done
    filtered_semesters = {sem: node for sem, node in sem_data.items() if sem.upper() != "NULL"}
    sorted_semesters = sorted(filtered_semesters.keys(), key=semester_sort_key)

    semesters, gpas, cgpas, top_courses = [], [], [], []

    for sem in sorted_semesters:
        node = filtered_semesters[sem]
        if not node.courses:
            continue
        avg_gpa = node.gpa
        deviations = [(abs(c.gpa - avg_gpa), c.course) for c in node.courses]
        max_deviation_course = max(deviations, default=(0, "N/A"))[1]
        semesters.append(sem)
        gpas.append(node.gpa)
        cgpas.append(node.cgpa)
        top_courses.append(max_deviation_course)

    if semesters:
        semesters_list, gpas, cgpas, most_off_track = [], [], [], []

        for sem in sorted_semesters:
            node = filtered_semesters[sem]
            if not node.courses:
                continue

            avg_gpa = node.gpa
            lowest_course = min(node.courses, key=lambda c: c.gpa)
            lowest_course_str = f"{lowest_course.course} ({lowest_course.gpa:.2f})"

            semesters_list.append(sem)
            gpas.append(node.gpa)
            cgpas.append(node.cgpa)
            most_off_track.append(lowest_course_str)

        df = pd.DataFrame({
            "Semester": semesters_list,
            "GPA": gpas,
            "CGPA": cgpas,
            "Most Off-Track Course": most_off_track
        })


        fig_gpa = px.line(
            df,
            x="Semester",
            y="GPA",
            markers=True,
            title="GPA Trend Over Semesters",
            hover_data={
                "Semester": False, 
                "GPA": True,
                "Most Off-Track Course": True,
            }
        )
        fig_gpa.update_layout(
            yaxis=dict(range=[0, 4]),
            template="plotly_white",
            hoverlabel=dict(bgcolor="black", font_size=14, font_family="Arial")
        )

        # CGPA Trend plot
        fig_cgpa = px.line(
            df,
            x="Semester",
            y="CGPA",
            markers=True,
            title="CGPA Trend Over Semesters"
        )
        fig_cgpa.update_layout(
            yaxis=dict(range=[0, 4]),
            template="plotly_white"
        )

        # Show both charts
        st.plotly_chart(fig_gpa, use_container_width=True)
        st.plotly_chart(fig_cgpa, use_container_width=True)



# ========== TAB 5 ==========
with tab5:
    st.header("🚀 Unlocked Courses Explorer")

    unlocked, unlocks_by = get_unlocked_courses(st.session_state.courses_done)
    comp_cod_session, _ = get_session_cod_sets(st.session_state.courses_done)

    col1, col2 = st.columns(2)

    dept = st.session_state.get("dept", "CSE")
    core_set = core if dept == "CSE" else core - cs_elective

    with col1:
        st.subheader("✅ Unlocked Core Courses")
        core_unlocked = sorted([c for c in unlocked if c in core_set])
        for course in core_unlocked:
            unlocked_list = unlocks_by.get(course, [])
            st.write(f"• {course}  ⇒  unlocks: {', '.join(unlocked_list) if unlocked_list else 'None'}")

    with col2:
        st.subheader("📘 Unlocked Compulsory COD Courses")

        comp_cod_unlocked = sorted([
            c for c in unlocked
            if c in comp_cod_session and c not in st.session_state.courses_done
        ])
        if comp_cod_unlocked:
            st.write("The following compulsory COD courses are now unlocked:")
            for course in comp_cod_unlocked:
                note = " _(Suggested to complete at TARC)_" if course in tarc else ""
                st.write(f"• {course}{note}")
        else:
            st.write("No compulsory COD courses are left.")

    st.markdown("---")
    st.markdown("In order to check which COD course you should take, please check the COD Planner")


RESOURCE_DIR = "resources"
from utils_parser import get_all_course_codes, load_course_resources
import os

RESOURCE_DIR = "resources"

def get_courses_with_resources():
    valid_courses = []
    for code in get_all_course_codes():
        data = load_course_resources(code, resource_dir=RESOURCE_DIR)
        if not data:
            continue
        has_resources = bool(data.get("resources"))
        has_mid = bool(data.get("previous_questions", {}).get("mid"))
        has_final = bool(data.get("previous_questions", {}).get("final"))
        if has_resources or has_mid or has_final:
            valid_courses.append(code)
    return sorted(valid_courses)

with tab6:
    st.header("📚 Course Resources & Previous Questions")

    course_options = get_courses_with_resources()
    if not course_options:
        st.info("No resource-rich courses available.")
    else:
        selected = st.selectbox("🔍 Search Course", options=course_options)

        if selected:
            data = load_course_resources(selected, resource_dir=RESOURCE_DIR)
            st.subheader(data.get("title", selected))

            if data.get("resources"):
                st.markdown("### 📂 Resources")
                for item in data["resources"]:
                    icon = "📁" if item["type"] == "folder" else "🔗"
                    st.markdown(f"{icon} [{item['name']}]({item['link']})")

            mid = data.get("previous_questions", {}).get("mid")
            final = data.get("previous_questions", {}).get("final")

            if mid or final:
                st.markdown("### 📝 Previous Questions")
                if mid:
                    st.markdown(f"🧪 [Midterm Questions]({mid})")
                if final:
                    st.markdown(f"🧠 [Final Questions]({final})")

#=============TAB 7==============
with tab7:
    st.header("Completed Courses Breakdown")

    courses_done = st.session_state.courses_done
    comp_cod_session, arts_st_session = get_session_cod_sets(courses_done)

    core_data = []
    comp_cod_data = []
    elective_data = []
    cod_data = []

    dept = st.session_state.get("dept", "CSE")
    core_set = core if dept == "CSE" else core - cs_elective

    for code in sorted(courses_done.keys()):
        if code in core_set:
            core_data.append({"Course Code": code})
        elif code in comp_cod_session:
            comp_cod_data.append({"Course Code": code})
        elif code.startswith("CSE") and code not in core_set and code not in comp_cod_session:
            elective_data.append({"Course Code": code})
        elif code in cst_st:
            cod_data.append({"Course Code": code, "Stream": "CST"})
        elif code in arts_st_session:
            cod_data.append({"Course Code": code, "Stream": "Arts"})
        elif code in ss_st:
            cod_data.append({"Course Code": code, "Stream": "Social Sciences"})
        elif code in science_st:
            cod_data.append({"Course Code": code, "Stream": "Science"})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader(f"Core Courses ({len(core_data)})")
        if core_data:
            df_core = pd.DataFrame(core_data)
            df_core.index = range(1, len(df_core) + 1)
            st.dataframe(df_core, use_container_width=True, height=300)
        else:
            st.info("No core courses completed.")

    with col2:
        st.subheader(f"Compulsory COD ({len(comp_cod_data)})")
        if comp_cod_data:
            df_comp = pd.DataFrame(comp_cod_data)
            df_comp.index = range(1, len(df_comp) + 1)
            st.dataframe(df_comp, use_container_width=True, height=300)
        else:
            st.info("No compulsory core courses completed.")

    with col3:
        st.subheader(f"COD Courses ({len(cod_data)})")
        if cod_data:
            df_cod = pd.DataFrame(cod_data).sort_values(by=["Stream", "Course Code"])
            df_cod.index = range(1, len(df_cod) + 1)
            st.dataframe(df_cod, use_container_width=True, height=300)
        else:
            st.info("No COD courses completed.")

    with col4:
        st.subheader(f"Electives ({len(elective_data)})")
        if elective_data:
            df_elec = pd.DataFrame(elective_data)
            df_elec.index = range(1, len(df_elec) + 1)
            st.dataframe(df_elec, use_container_width=True, height=300)
        else:
            st.info("No elective courses completed.")

import datetime
import random

QUOTES = [
    "It's dangerous to go alone, take this semester seriously.",
    "Finish the fight.",
    "Hard work is the real power-up.",
    "Every season is exam season. Prepare accordingly.",
    "You were born to be the very best, like no one ever was.",
    "Failure doesn't mean defeat, just a checkpoint.",
    "The cake may be a lie, but your potential isn’t.",
    "The only choice you have is how good you WILL do in your test. We always have a choice. Make the right choice.",
    "Even the smallest person can change the course of CGPA.",
    "Believe in the me that believes in you!",
    "You have the power to rewrite your story.",
    "Study. Rest. 'Sir ek mark dile grade bare'. Repeat.",
    "No matter the odds, you keep going. That's your superpower.",
    "Academic success is forged in fire and coffee.",
    "The Force will be with you, always.",
    "You can do this all day.",
    "Not all those who wander are lost, some are just changing majors.",
    "Push the payload. Pass the semester.",
    "A hero is someone who gets up, even when CGPA says no.",
    "Nothing is true, everything is permitted, except plag.",
    "You don’t need a Senzu bean. You just need a plan.",
    "When life gives you fetch quests, turn them into achievements.",
    "FUS RO PASS!",
    "You are more than your save files.",
    "This semester... we ride.",
    "DEEZ NUTS",
    "SHINZOU WO SASAGEYO",
    "Tatakae."
]


def get_quote_of_the_day():
    now = datetime.datetime.now()
    seed = now.strftime('%Y-%m-%d-%H') + f"-{now.minute // 1 * 2}"
    random.seed(seed)
    return random.choice(QUOTES)

quote = get_quote_of_the_day()

st.markdown("""
<style>
/* Eliminate extra bottom space */
section.main {
    padding-bottom: 0 !important;
}

/* Footer container with subtle box */
.footer-container {
    background-color: rgba(255, 255, 255, 0.02);
    padding: 1rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    color: #ccc;
}

/* Flex layout */
.footer-flex {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 1.5rem;
}

/* Left side */
.footer-left {
    max-width: 480px;
    line-height: 1.5;
}

.footer-left strong {
    font-size: 14px;
    color: white;
}

.footer-left a {
    display: inline-block;
    margin-right: 12px;
    margin-top: 4px;
    color: #80DFFF;
    text-decoration: none;
    font-weight: 500;
    font-size: 13px;
}

.footer-left a:hover {
    color: white;
}

.footer-links {
    margin-top: 8px;
}

.footer-note {
    margin-top: 8px;
    font-style: italic;
    font-size: 12px;
    color: #aaa;
}

/* Right side (quote) */
.footer-right {
    color: #80DFFF;
    font-style: italic;
    font-size: 24px;
    max-width: 420px;
    padding-top: 4px;
    margin-left: 20px;
    text-align: left;
}

/* Responsive tweaks */
@media (max-width: 768px) {
    .footer-flex {
        flex-direction: column;
        text-align: center;
    }
    .footer-right {
        text-align: center;
        margin-left: 0;
        margin-top: 1rem;
    }
    .footer-note {
        text-align: center;
    }
}
</style>

<div class="footer-container">
  <div class="footer-flex">
    <div class="footer-left">
        Built with ❤️ by <strong>Dihan Islam Dhrubo</strong><br>
        <a href="https://github.com/xDhruboVai/BRACU-Gradesheet-Analyzer-CSE-" target="_blank">🔗 GitHub Repo</a>
        <a href="https://www.linkedin.com/in/dihan-islam-dhrubo-79a904249/" target="_blank">💼 LinkedIn</a>
        <a href="https://www.facebook.com/dihanislam.dhrubo.5/" target="_blank">📘 Facebook</a>
        <div class="footer-links">
            <a href="https://youtu.be/RPpUlPvq5Fo" target="_blank">📺 Tutorial</a><br>
            <a href="https://forms.gle/U4yiB45m8vSDAwU3A" target="_blank">💬 Suggest / Report</a>
        </div>
        <div class="footer-note">
            📌 Bookmark the site · 🙏 Thanks for using the app!
        </div>
    </div>
    <div class="footer-right">
        “{quote}”
    </div>
  </div>
</div>
""".replace("{quote}", quote), unsafe_allow_html=True)

st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
