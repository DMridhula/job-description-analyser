
import streamlit as st
import database
import analyser
import integratai

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Job Description Analyser",
    page_icon="🎯",
    layout="wide"
)

# ---------------- VIOLET THEME ----------------

st.markdown("""
<style>
h1, h2, h3 {
    color: #172554 !important;
}

/* Sidebar navigation label */
[data-testid="stSidebar"] label {
    color: #172554;
    font-weight: 600;
}

.stButton > button {
    background-color: #8B5CF6;
    color: white;
    border: 1px solid #8B5CF6;
    border-radius: 8px;
    font-weight: 600;
    transition: background-color 0.2s ease;
}

.stButton > button:hover {
    background-color: #6D28D9;
    color: white;
    border-color: #6D28D9;
}

.stButton > button:focus:not(:active) {
    color: white;
    border-color: #A78BFA;
    box-shadow: 0 0 0 2px #DDD6FE;
}

[data-testid="stSidebar"] {
    border-right: 1px solid #E9D5FF;
}

[data-testid="stMetric"] {
    background-color: rgba(139, 92, 246, 0.08);
    border: 1px solid rgba(139, 92, 246, 0.25);
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- INITIAL SETUP ----------------

database.create_database()

# Keep analysis results and AI answers between reruns.
if "analysis_results" not in st.session_state:
    st.session_state["analysis_results"] = None

if "job_details" not in st.session_state:
    st.session_state["job_details"] = None

if "analyzed_job_description" not in st.session_state:
    st.session_state["analyzed_job_description"] = ""

if "ai_job_insights" not in st.session_state:
    st.session_state["ai_job_insights"] = None

if "job_ai_answer" not in st.session_state:
    st.session_state["job_ai_answer"] = None

# ---------------- HEADER ----------------

st.title("Job Description Analyser")
st.caption("Your personal job analysis dashboard")

page = st.sidebar.radio(
    "Navigation",
    ["My Career Profile", "Analyse Job"]
)

saved_skills, saved_projects, saved_certifications = (
    database.load_profile()
)

# ---------------- CAREER PROFILE ----------------

if page == "My Career Profile":

    st.header("My Career Profile")

    skills = st.text_area(
        "My Skills",
        value=saved_skills
    )

    projects = st.text_area(
        "My Projects",
        value=saved_projects
    )

    certifications = st.text_area(
        "My Certifications",
        value=saved_certifications
    )

    if st.button("Save My Profile", type="primary"):

        database.save_profile(
            skills,
            projects,
            certifications
        )

        st.success("Profile saved successfully!")

# ---------------- JOB ANALYSIS PAGE ----------------

elif page == "Analyse Job":

    st.header("Analyse a Job Description")

    job_description = st.text_area(
        "Paste the complete job description",
        height=300,
        placeholder="Paste the job description here...",
        key="job_description_input"
    )

    if st.button("Analyse Job", type="primary"):

        if not job_description.strip():

            st.warning("Please paste a job description.")

        else:

            # Save the analysis so it survives button reruns.
            st.session_state["analyzed_job_description"] = (
                job_description
            )

            st.session_state["analysis_results"] = (
                analyser.analyse_job(
                    job_description,
                    saved_skills
                )
            )

            st.session_state["job_details"] = (
                analyser.analyse_job_details(
                    job_description
                )
            )

            # Clear AI answers from the previous job.
            st.session_state["ai_job_insights"] = None
            st.session_state["job_ai_answer"] = None
            st.session_state["job_ai_question"] = ""

    # Display saved analysis whenever it exists.
    # This is deliberately outside the Analyse Job button.

    results = st.session_state["analysis_results"]
    details = st.session_state["job_details"]

    analyzed_jd = st.session_state["analyzed_job_description"]

    if results is not None and details is not None:

        # -------- JOB OVERVIEW --------

        st.divider()
        st.subheader("Job Overview")

        st.write(
            "**Possible Job Title:**",
            details["job_title"]
        )

        st.write(
            "**Experience:**",
            details["experience"]
        )

        st.write(
            "**Salary / CTC:**",
            details["salary"]
        )

        # -------- SKILL MATCH --------

        st.divider()
        st.subheader("Your Skill Match")

        st.metric(
            "Recognized Skill Match",
            f"{results['match_percentage']}%"
        )

        st.caption(
            "Based only on recognized skills, "
            "not overall job suitability."
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("**Skills You Have**")

            if results["matched_skills"]:
                for skill in results["matched_skills"]:
                    st.write(f"✓ {skill}")
            else:
                st.write("No recognized matches.")

        with col2:

            st.markdown("**Skills You Need to Learn**")

            if results["missing_skills"]:
                for skill in results["missing_skills"]:
                    st.write(f"• {skill}")
            else:
                st.write("No recognized skill gaps.")

        # -------- SKILL PRIORITIES --------

        st.divider()
        st.subheader("Required Skills and Priorities")

        for priority, skills_list in details["priorities"].items():

            with st.expander(
                f"{priority} ({len(skills_list)})",
                expanded=True
            ):

                if skills_list:

                    for skill in skills_list:

                        if skill in results["missing_skills"]:
                            st.write(f"• {skill} — Missing")

                        elif skill in results["matched_skills"]:
                            st.write(f"• {skill} — You have this")

                        else:
                            st.write(f"• {skill}")

                else:
                    st.write("No skills identified.")

        # -------- RESPONSIBILITIES --------

        st.divider()
        st.subheader("Key Roles and Responsibilities")

        if details["responsibilities"]:

            for responsibility in details["responsibilities"]:
                st.write(f"• {responsibility}")

        else:

            st.info(
                "No clear responsibilities detected. "
                "Review the original job description."
            )

        # -------- ADDITIONAL INFORMATION --------

        st.divider()
        st.subheader("Additional Important Information")

        if details["additional_info"]:

            for item in details["additional_info"]:
                st.write(f"• {item}")

        else:

            st.write(
                "No explicitly labelled additional "
                "details were detected."
            )

        # -------- ASK AI ABOUT THIS JOB --------

        st.divider()
        st.subheader("Ask AI About This Job")

        st.write(
            "Ask questions about the job, your skill gaps, "
            "or how to prepare for the role."
        )

        user_question = st.text_input(
            "Your question",
            key="job_ai_question",
            placeholder=(
                "e.g. How can I learn the missing skills?"
            )
        )

        if st.button("Ask AI", type="primary"):

            if not user_question.strip():

                st.warning("Please enter a question.")

            else:

                with st.spinner(
                    "AI is preparing your answer..."
                ):

                    try:

                        profile_text = f"""
Skills: {saved_skills}
Projects: {saved_projects}
Certifications: {saved_certifications}
"""

                        answer = integratai.ask_gemini(
                            analyzed_jd,
                            profile_text,
                            user_question
                        )

                        if answer and answer.strip():

                            st.session_state["job_ai_answer"] = (
                                answer
                            )

                        else:

                            st.warning(
                                "The AI returned an empty response. "
                                "Please try again."
                            )

                    except Exception as e:

                        st.error(
                            f"Could not get an AI answer: {e}"
                        )

        if st.session_state["job_ai_answer"]:

            st.markdown("### AI Response")

            st.markdown(
                st.session_state["job_ai_answer"]
            )

        # -------- NEXT STEPS --------

        st.divider()
        st.subheader("Your Next Steps")

        if results["missing_skills"]:

            st.write(
                "Prioritize the missing skills marked as high "
                "priority, then work through the remaining gaps."
            )

        else:

            st.write(
                "No gaps were found in the recognized skills. "
                "Review the full job requirements before deciding "
                "you are fully qualified."
            )

        if not details["salary"].startswith("Not specified"):

            st.info(
                "Verify the salary details and whether the amount "
                "is fixed pay, variable pay, or total CTC."
            )
