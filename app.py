import json
import streamlit as st
from app.services.resume_analysis import analyze_resume, extract_text

st.set_page_config(page_title="Career Intelligence | Resume Advisor", layout="wide")

st.title("🚀 Career Intelligence Assistant")
st.caption("Resume parsing, strengths, and intent-driven career recommendations.")

with st.sidebar:
    st.header("Inputs")
    resume_file = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    intent = st.radio(
        "Intent",
        options=["A", "B", "C", "D"],
        format_func=lambda x: {
            "A": "Explore alternate roles",
            "B": "Find a promotion / next-level role",
            "C": "Transition to a different role",
            "D": "Unsure – explore market opportunities",
        }[x],
    )
    target_role = st.text_input("Target role (if intent C or B)", placeholder="e.g., Enterprise Architect")
    current_location = st.text_input("Current location", placeholder="City, State/Country")
    preferred_location = st.text_input("Preferred location", placeholder="Remote / Hybrid / Onsite")
    years_experience = st.number_input("Years of experience", min_value=0.0, value=20.0, step=0.5)
    work_mode = st.selectbox("Work mode", ["remote", "hybrid", "onsite", "unspecified"], index=0)

    analyze_btn = st.button("Analyze Resume")


def render_recommendations(recs):
    st.subheader("Career Recommendations")
    for rec in recs:
        with st.container():
            st.markdown(f"**{rec['role']}** — Match: {rec['match']}%")
            st.caption(rec.get("why"))
            cols = st.columns(2)
            with cols[0]:
                st.markdown("**Transferable Strengths**")
                for item in rec.get("matched", []):
                    st.write(f"• {item}")
            with cols[1]:
                st.markdown("**Gaps / Upskilling**")
                if rec.get("gaps"):
                    for gap in rec["gaps"]:
                        st.write(f"• {gap}")
                else:
                    st.write("• Minimal gaps detected")
            st.markdown("---")


def render_list(title: str, items):
    if not items:
        return
    st.subheader(title)
    for item in items:
        st.write(f"• {item}")


if analyze_btn:
    if not resume_file:
        st.error("Please upload a resume file first.")
    else:
        try:
            raw_bytes = resume_file.read()
            resume_text = extract_text(raw_bytes, resume_file.name)
            context = {
                "target_role": target_role,
                "current_location": current_location,
                "preferred_location": preferred_location,
                "work_mode": work_mode,
                "years_experience": years_experience,
            }
            result = analyze_resume(resume_text, intent, context)

            # Structured Output
            st.success("Analysis complete.")
            st.subheader("Resume Summary")
            st.write(result["summary"])

            render_list("Identified Strengths", result.get("strengths", []))
            render_recommendations(result.get("recommendations", []))
            render_list("Gap Analysis", result.get("gaps", []))
            render_list("Action Plan", result.get("action_plan", []))
            render_list("Next Steps", result.get("next_steps", []))

            # Download JSON
            st.download_button(
                label="Download Analysis (JSON)",
                data=json.dumps(result, indent=2),
                file_name="career_analysis.json",
                mime="application/json",
            )

            with st.expander("Raw Parsed Text"):
                st.text(resume_text[:8000])

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
