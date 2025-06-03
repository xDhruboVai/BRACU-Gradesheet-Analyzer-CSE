import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils_parser import (
    extract, add_course, remove_course, simulate_retake,
    cgpa_projection, cgpa_planner, cod_planner, course_node,
    courses_done, semesters_done, get_unlocked_courses
)
from shared_data import(
    preq, arts_st, cst_st, core, science_st, ss_st, labs
)

# --- UI Setup ---
st.set_page_config(page_title="Academic Dashboard", layout="wide")

st.markdown("""
    <style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- State Setup ---
if "name" not in st.session_state:
    st.session_state.name = ""
    st.session_state.id = ""
    st.session_state.uploaded = False
    st.session_state.regrades = {}
    st.session_state.retakes = {}
    st.session_state.original_gpas = {}

# --- Sidebar: Upload Transcript ---
st.sidebar.title("Transcript Upload")
pdf = st.sidebar.file_uploader("Upload your transcript", type="pdf")

if pdf and not st.session_state.uploaded:
    with open("temp.pdf", "wb") as f:
        f.write(pdf.read())
    name, sid, _, _ = extract("temp.pdf")
    st.session_state.name = name
    st.session_state.id = sid
    st.session_state.uploaded = True

    st.session_state.original_gpas = {c: courses_done[c].gpa for c in courses_done}
    st.session_state.retakes = {}
    st.session_state.regrades = {}

    st.success("Transcript processed.")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Courses & Retake", 
    "CGPA Planner", 
    "COD Planner",
    "Visual Analytics",
    "Unlocked Courses"
])


# -- Initialization --
if "added_courses" not in st.session_state:
    st.session_state.added_courses = set()
if "retakes" not in st.session_state:
    st.session_state.retakes = {}
if "original_gpas" not in st.session_state:
    st.session_state.original_gpas = {}
if "regrades" not in st.session_state:
    st.session_state.regrades = {}

# ========== TAB 1 ==========
with tab1:
    st.header("Student & Academic Info")
    col1, col2, col3 = st.columns([3, 3, 1])

    blur = col1.checkbox("Blur personal info")
    refresh = col3.button("🔄 Refresh Info")

    def calculate_cgpa():
        total_credits = sum(c.credit for c in courses_done.values())
        total_points = sum(c.gpa * c.credit for c in courses_done.values())
        return (round(total_points / total_credits, 2) if total_credits else 0.0, total_credits)

    def refresh_info():
        cgpa, credits = calculate_cgpa()
        st.session_state.cgpa = cgpa
        st.session_state.total_credits = credits

    # Auto-refresh only once on first load
    if "cgpa" not in st.session_state:
        refresh_info()

    if refresh:
        refresh_info()
        st.success("Student info refreshed!")

    if st.session_state.get("uploaded", False):
        name = '[Hidden]' if blur else st.session_state.get("name", "Unknown")
        student_id = '[Hidden]' if blur else st.session_state.get("id", "Unknown")

        st.text(f"Name: {name}")
        st.text(f"ID: {student_id}")
        st.metric("Credits Earned", st.session_state.total_credits)
        st.metric("CGPA", st.session_state.cgpa)

        st.markdown("---")
        col_left, col_right = st.columns(2)

        # ----------------- Add a Course -----------------
        with col_left:
            st.subheader("➕ Add a Course")
            new_code = st.text_input("New Course Code", key="new_course")
            new_gpa = st.number_input("GPA", min_value=0.0, max_value=4.0, step=0.01, key="new_course_gpa")
            can_add = new_code and new_code not in courses_done

            if st.button("Add Course", disabled=not can_add):
                add_course(new_code, new_gpa)
                st.session_state.original_gpas[new_code] = new_gpa  # track for rollback
                st.session_state.added_courses.add(new_code)
                refresh_info()
                st.success(f"Added {new_code} with GPA {new_gpa:.2f}")

        # ----------------- Retake a Course -----------------
        with col_right:
            st.subheader("🔁 Retake a Course")
            retake_options = [
                code for code, node in courses_done.items()
                if node.gpa < 4.0 and code not in st.session_state.retakes
            ]
            course_to_retake = st.selectbox("Select Course to Retake", retake_options, key="retake_select")
            new_gpa = st.number_input("New GPA", min_value=0.0, max_value=4.0, step=0.01, key="retake_gpa")

            if st.button("Retake Course", disabled=not course_to_retake):
                st.session_state.retakes[course_to_retake] = new_gpa
                if course_to_retake not in st.session_state.original_gpas:
                    st.session_state.original_gpas[course_to_retake] = courses_done[course_to_retake].gpa
                add_course(course_to_retake, new_gpa)
                refresh_info()
                st.success(f"Retaken {course_to_retake} with new GPA {new_gpa:.2f}")

        st.markdown("---")
        st.subheader("🗑️ Remove a Course")

        removable_courses = list(st.session_state.added_courses.union(st.session_state.retakes.keys()))
        selected_remove = st.multiselect("Select course(s) to remove", options=removable_courses)

        if st.button("Remove Selected Course(s)", disabled=not selected_remove):
            for course in selected_remove:
                # If it was a retake, restore the original GPA
                if course in st.session_state.retakes:
                    # Step 1: Remove retake (virtual semester entry)
                    remove_course(course)
                    
                    # Step 2: Restore original GPA
                    original_gpa = st.session_state.original_gpas.get(course)
                    if original_gpa is not None:
                        original_credit = 4 if course == "CSE400" else 3
                        courses_done[course] = course_node(course, gpa=original_gpa)
                        courses_done[course].credit = original_credit

                    # Cleanup state
                    st.session_state.retakes.pop(course, None)
                    st.session_state.regrades.pop(course, None)

                elif course in st.session_state.added_courses:
                    st.session_state.added_courses.remove(course)
                    st.session_state.original_gpas.pop(course, None)
                    remove_course(course)  # Remove the course completely
            refresh_info()
            st.success(f"Removed: {', '.join(selected_remove)}")


    else:
        st.info("Upload a transcript to begin.")


# ========== TAB 2 ==========
with tab2:
    st.header("📊 CGPA Planner & Projection")

    with st.form("cgpa_planner_form"):
        st.markdown("🎯 **Set your target and plan your academic path**")

        col1, col2 = st.columns(2)
        target_cgpa = col1.number_input("🎯 Target CGPA", min_value=0.0, max_value=4.0, step=0.01)
        semesters = col2.number_input("📆 Future Semesters", min_value=0, step=1)
        courses_per_sem = st.slider("📚 Courses per Semester", min_value=0, max_value=6, value=4)

        submitted = st.form_submit_button("📈 Run CGPA Planner")
        if submitted:
            result = cgpa_planner(target_cgpa=target_cgpa, semesters=semesters, courses_per_sem=courses_per_sem)
            st.markdown("### 📋 Planner Result")
            st.metric("Max Possible CGPA", result.get("max_cgpa", 0.0))

            if "required_avg_gpa" in result:
                st.metric("Required Avg GPA", result["required_avg_gpa"])
            if "message" in result:
                st.info(result["message"])

    st.markdown("---")
    st.subheader("🔍 Max CGPA Projection")

    if st.button("Run Max CGPA Projection"):
        proj = cgpa_projection(target_cgpa=target_cgpa)
        st.metric("Max Achievable CGPA", proj.get("max_cgpa", 0.0))
        if "message" in proj:
            st.info(proj["message"])

# ========== TAB 3 ==========
with tab3:
    st.header("📚 COD Planner")

    if st.button("🎯 Generate COD Plan"):
        cod = cod_planner()
        taken_courses = set(courses_done.keys())

        # Summary Overview - Clean 2x2 Grid
        st.markdown("**Total CODs Completed:**")
        st.metric(label="", value=f"{cod['total_taken']} / 5")
        st.markdown("### 📊 Current COD Status")
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        col1.metric("🎨 Arts", cod["arts"])
        col2.metric("🌍 Social Sciences", cod["ss"])
        col3.metric("💻 CST", cod["cst"])
        col4.metric("🧪 Science", cod["science"])

       

        st.markdown("---")

        # Recommended Streams
        st.markdown("### 💡 Recommended Streams to Prioritize")
        recommended_streams = []

        if cod["arts"] == 0:
            recommended_streams.append("Arts (Required)")
        if cod["ss"] == 0:
            recommended_streams.append("Social Sciences (Required)")
        if cod["cst"] == 0:
            recommended_streams.append("CST (Choose at most one)")
        if cod["science"] == 0:
            recommended_streams.append("Science (Optional)")

        if cod["total_taken"] >= 5:
            st.success("✅ You have completed the maximum number of CODs allowed (5).")
        else:
            if recommended_streams:
                for r in recommended_streams:
                    st.markdown(f"- {r}")
            else:
                st.info("You’ve met all stream coverage requirements. Pick any remaining CODs to reach 5.")

        st.markdown("---")

        # Available CODs by Stream
        st.markdown("### 📚 Remaining COD Courses by Stream")
        stream_map = {
            "🎨 Arts": arts_st,
            "🌍 Social Sciences": ss_st,
            "💻 CST": cst_st,
            "🧪 Science": science_st
        }

        for stream_label, course_set in stream_map.items():
            remaining = sorted([c for c in course_set if c not in taken_courses])
            with st.expander(f"{stream_label} ({len(remaining)} remaining)"):
                if remaining:
                    st.write("• " + "\n• ".join(remaining))
                else:
                    st.write("✅ All courses in this stream have been completed.")

        if cod["message"]:
            st.info(cod["message"])



# ========== TAB 4 ==========
with tab4:
    st.header("📊 Visual Analytics Dashboard")

    # === 3D Pie Chart for Credit Completion ===
    st.subheader("🎯 Credit Completion")

    completed = st.session_state.total_credits
    remaining = 136 - completed

    fig_pie = go.Figure(data=[go.Pie(
        labels=["Completed", "Remaining"],
        values=[completed, remaining],
        hole=0.3,
        marker=dict(colors=['#00cc96', '#EF553B']),
    )])
    fig_pie.update_traces(textinfo='label+percent', pull=[0.1, 0], rotation=45)
    fig_pie.update_layout(
        title="Credits Earned vs Remaining (out of 136)",
        showlegend=True,
        template="plotly_dark",
        height=400,
        margin=dict(t=40, b=0, l=0, r=0),
        scene_camera_eye=dict(x=0.5, y=1.5, z=0.5)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    # === GPA & CGPA Trend Line Chart ===
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

    # Filter and sort valid semesters
    filtered_semesters = {
        sem: node for sem, node in semesters_done.items()
        if sem.upper() != "NULL"
    }
    sorted_semesters = sorted(filtered_semesters.keys(), key=semester_sort_key)

    # Prepare data with deviation info
    semesters = []
    gpas = []
    cgpas = []
    top_courses = []

    for sem in sorted_semesters:
        node = filtered_semesters[sem]
        if not node.courses:
            continue

        avg_gpa = node.gpa
        deviations = [(abs(course.gpa - avg_gpa), course.course) for course in node.courses]
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

        # --- GPA Trend Chart with Hover Info ---
        fig_gpa = px.line(
            df,
            x="Semester",
            y="GPA",
            markers=True,
            line_shape="spline",
            title="📈 GPA Trend Over Semesters",
            hover_data={"Top Deviant Course": True, "GPA": True, "Semester": True}
        )
        fig_gpa.update_layout(
            yaxis=dict(range=[0, 4]),
            template="plotly_white",
            margin=dict(l=20, r=20, t=60, b=20),
            title_x=0.5
        )
        st.plotly_chart(fig_gpa, use_container_width=True)

        # --- CGPA Trend Chart ---
        fig_cgpa = px.line(
            df,
            x="Semester",
            y="CGPA",
            markers=True,
            line_shape="spline",
            title="📊 CGPA Trend Over Semesters",
            hover_data={"Semester": True, "CGPA": True}
        )
        fig_cgpa.update_layout(
            yaxis=dict(range=[0, 4]),
            template="plotly_white",
            margin=dict(l=20, r=20, t=60, b=20),
            title_x=0.5
        )
        st.plotly_chart(fig_cgpa, use_container_width=True)

    else:
        st.info("No semester data available for trend analysis.")



# ========== TAB 5 ==========
with tab5:
    st.header("🚀 Unlocked Courses Explorer")

    # Correct prerequisite resolution
    def get_unlocked_courses():
        completed = set(courses_done.keys())

        prereq_map = {}
        reverse_unlock_map = {}

        # Build full prerequisite map and reverse unlock map
        all_courses = set(preq.keys()) | {c for v in preq.values() for c in v}

        for course in all_courses:
            prereq_map.setdefault(course, [])

        for course, unlocks in preq.items():
            for unlocked in unlocks:
                prereq_map[unlocked].append(course)
                reverse_unlock_map.setdefault(course, []).append(unlocked)

        unlocked_now = set()
        for course in prereq_map:
            if course in completed:
                continue
            prereqs = prereq_map[course]
            if all(p in completed for p in prereqs):
                unlocked_now.add(course)

        # Also: Add all COD courses not in prereq_map and not done
        cod_pool = cst_st | ss_st | arts_st | science_st
        for course in cod_pool:
            if course not in prereq_map and course not in completed:
                unlocked_now.add(course)

        return unlocked_now, reverse_unlock_map


    unlocked_courses, unlocks_by = get_unlocked_courses()

    # Core Courses
    st.subheader("✅ Unlocked Core Courses")
    core_unlocked = sorted([c for c in unlocked_courses if c in core])
    if core_unlocked:
        for course in core_unlocked:
            unlocked = unlocks_by.get(course, [])
            st.write(f"• {course}  ⇒  unlocks: {', '.join(unlocked) if unlocked else 'None'}")
    else:
        st.info("No core courses unlocked yet.")

    # COD Courses by Stream
    st.markdown("---")
    st.subheader("🎯 Unlocked COD Courses by Stream")

    cod_streams = {
        "Arts": arts_st,
        "SS": ss_st,
        "CST": cst_st,
        "Science": science_st
    }

    for stream, course_set in cod_streams.items():
        stream_courses = sorted([c for c in unlocked_courses if c in course_set])
        with st.expander(f"{stream} ({len(stream_courses)} available)"):
            if stream_courses:
                st.write(", ".join(stream_courses))
            else:
                st.write("No courses unlocked yet.")
