import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils_parser import (
    extract, add_course, remove_course, simulate_retake,
    cgpa_projection, cgpa_planner, cod_planner, course_node,
    get_unlocked_courses
)
from shared_data import (
    preq, arts_st, cst_st, core, science_st, ss_st, labs
)

# Page config
st.set_page_config(
    page_title="BRACU Gradesheet Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme and header
st.title("📊 BRACU Gradesheet Analyzer")
st.markdown("Analyze your BRAC University transcript, calculate CGPA, visualize trends and plan courses.")

# CSS for dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

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

# Upload transcript
st.sidebar.title("Transcript Upload")
pdf = st.sidebar.file_uploader("Upload your transcript", type="pdf")

if pdf and not st.session_state.uploaded:
    with open("temp.pdf", "wb") as f:
        f.write(pdf.read())
    name, sid, c_done, s_done = extract("temp.pdf")
    st.session_state.name = name
    st.session_state.id = sid
    st.session_state.uploaded = True
    st.session_state.courses_done = c_done
    st.session_state.semesters_done = s_done
    st.session_state.original_gpas = {c: n.gpa for c, n in c_done.items()}
    st.success("Transcript processed.")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Courses & Retake", "CGPA Planner", "COD Planner", "Visual Analytics", "Unlocked Courses"
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

    col1, col2, col3 = st.columns([3, 3, 1])
    blur = col1.checkbox("Blur personal info")
    refresh = col3.button("🔄 Refresh Info")

    if refresh:
        refresh_info()
        st.success("Student info refreshed!")

    if st.session_state.uploaded:
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
            new_code = st.text_input("New Course Code", key="new_course")
            new_gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, step=0.01, key="new_course_gpa")
            can_add = new_code and new_code not in st.session_state.courses_done

            if st.button("Add Course", disabled=not can_add):
                add_course(new_code, new_gpa, st.session_state.courses_done, st.session_state.semesters_done)
                st.session_state.original_gpas[new_code] = new_gpa
                st.session_state.added_courses.add(new_code)
                refresh_info()
                st.success(f"Added {new_code} with GPA {new_gpa:.2f}")

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
                st.success(f"Retaken {course_to_retake} with new GPA {retake_gpa:.2f}")

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
            st.success(f"Removed: {', '.join(selected_remove)}")

    else:
        st.info("Upload a transcript to begin.")

# ========== TAB 2 ==========
with tab2:
    st.header("📊 CGPA Planner & Projection")
    with st.form("cgpa_planner_form"):
        col1, col2 = st.columns(2)
        target_cgpa = col1.number_input("🎯 Target CGPA", min_value=0.0, max_value=4.0, step=0.01)
        semesters = col2.number_input("📆 Future Semesters", min_value=0, step=1)
        courses_per_sem = st.slider("📚 Courses per Semester", min_value=0, max_value=6, value=4)
        submitted = st.form_submit_button("📈 Run CGPA Planner")

        if submitted:
            result = cgpa_planner(st.session_state.courses_done, target_cgpa, semesters, courses_per_sem)
            st.metric("Max Possible CGPA", result.get("max_cgpa", 0.0))
            if "required_avg_gpa" in result:
                st.metric("Required Avg GPA", result["required_avg_gpa"])
            if "message" in result:
                st.info(result["message"])

    st.markdown("---")
    st.subheader("🔍 Max CGPA Projection")

    if st.button("Run Max CGPA Projection"):
        proj = cgpa_projection(st.session_state.courses_done, target_cgpa)
        st.metric("Max Achievable CGPA", proj.get("max_cgpa", 0.0))
        if "message" in proj:
            st.info(proj["message"])

# ========== TAB 3 ==========
with tab3:
    st.header("📚 COD Planner")

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
            "Arts": arts_st,
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
    remaining = 136 - completed

    fig_pie = go.Figure(data=[go.Pie(
        labels=["Completed", "Remaining"],
        values=[completed, remaining],
        hole=0.3,
        marker=dict(colors=['#00cc96', '#EF553B']),
    )])
    fig_pie.update_traces(textinfo='label+percent')
    fig_pie.update_layout(
        title="Credits Earned vs Remaining (out of 136)",
        template="plotly_dark",
        height=400
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # GPA trend
    st.subheader("📈 GPA & CGPA Trend")

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
        df = pd.DataFrame({
            "Semester": semesters,
            "GPA": gpas,
            "CGPA": cgpas,
            "Top Deviant Course": top_courses
        })

        fig_gpa = px.line(df, x="Semester", y="GPA", markers=True, title="GPA Trend Over Semesters")
        fig_cgpa = px.line(df, x="Semester", y="CGPA", markers=True, title="CGPA Trend Over Semesters")

        fig_gpa.update_layout(yaxis=dict(range=[0, 4]), template="plotly_white")
        fig_cgpa.update_layout(yaxis=dict(range=[0, 4]), template="plotly_white")

        st.plotly_chart(fig_gpa, use_container_width=True)
        st.plotly_chart(fig_cgpa, use_container_width=True)

# ========== TAB 5 ==========
with tab5:
    st.header("🚀 Unlocked Courses Explorer")

    unlocked, unlocks_by = get_unlocked_courses(st.session_state.courses_done)

    st.subheader("✅ Unlocked Core Courses")
    core_unlocked = sorted([c for c in unlocked if c in core])
    for course in core_unlocked:
        unlocked_list = unlocks_by.get(course, [])
        st.write(f"• {course}  ⇒  unlocks: {', '.join(unlocked_list) if unlocked_list else 'None'}")

    st.markdown("---")
    st.subheader("COD Courses by Stream")

    cod_streams = {
        "Arts": arts_st,
        "Social Science": ss_st,
        "CST": cst_st,
        "Science": science_st
    }

    for stream, course_set in cod_streams.items():
        available = sorted([c for c in unlocked if c in course_set])
        with st.expander(f"{stream} ({len(available)} available)"):
            st.write(", ".join(available) if available else "No courses unlocked yet.")
