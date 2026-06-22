from pathlib import Path

import streamlit as st

from pages.dashboard import render_dashboard
from pages.interview_questions import render_interview_questions
from pages.learning_roadmap import render_learning_roadmap
from pages.recruiter_summary import render_recruiter_summary
from utils.gemini_analyzer import GeminiAnalyzer
from utils.pdf_reader import PDFReader
from utils.score_calculator import ResumeAnalysisEngine
from utils.text_cleaner import TextCleaner


APP_ROOT = Path(__file__).parent


def load_css() -> None:
    css_path = APP_ROOT / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def init_session_state() -> None:
    defaults = {
        "analysis_result": None,
        "resume_text": "",
        "jd_text": "",
        "ai_analysis": "",
        "interview_questions": "",
        "learning_roadmap": "",
        "recruiter_summary": "",
        "improvement_suggestions": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_sidebar() -> tuple:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="brand-mark">AI</div>
                <div>
                    <h2>ResumeIQ</h2>
                    <p>GenAI Resume Analyzer</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Upload Center")
        resume_file = st.file_uploader("Resume PDF", type=["pdf"], help="Upload the candidate resume.")
        jd_file = st.file_uploader("Job Description PDF", type=["pdf"], help="Optional: upload a JD PDF.")
        jd_text = st.text_area("Or paste Job Description", height=190, placeholder="Paste the target role description here...")

        st.markdown("### Navigation")
        page = st.radio(
            "Select workspace",
            ["Dashboard", "Interview Questions", "Learning Roadmap", "Recruiter Summary"],
            label_visibility="collapsed",
        )

        st.markdown(
            """
            <div class="sidebar-note">
                <strong>Portfolio Mode</strong>
                <span>ATS scoring, GenAI insights, recruiter summaries, and PDF reporting in one product surface.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    return resume_file, jd_file, jd_text, page


@st.cache_data(show_spinner=False)
def extract_pdf_text(file_bytes: bytes) -> str:
    return PDFReader().extract_text_from_bytes(file_bytes)


def build_analysis(resume_file, jd_file, pasted_jd: str) -> None:
    if not resume_file:
        return

    reader_error = None
    try:
        resume_text = extract_pdf_text(resume_file.getvalue())
    except Exception as exc:
        resume_text = ""
        reader_error = str(exc)

    jd_text = pasted_jd.strip()
    if jd_file:
        try:
            jd_text = extract_pdf_text(jd_file.getvalue())
        except Exception as exc:
            st.warning(f"Could not read JD PDF: {exc}")

    if reader_error:
        st.error(f"Could not read resume PDF: {reader_error}")
        return

    st.session_state.resume_text = resume_text
    st.session_state.jd_text = jd_text

    if resume_text and jd_text:
        engine = ResumeAnalysisEngine(TextCleaner())
        st.session_state.analysis_result = engine.analyze(resume_text, jd_text)


def render_hero(has_analysis: bool) -> None:
    status = "Analysis ready" if has_analysis else "Upload resume and JD to begin"
    st.markdown(
        f"""
        <section class="hero">
            <div>
                <span class="eyebrow">Premium GenAI SaaS Dashboard</span>
                <h1>AI Resume Analyzer for ATS, hiring, and interview readiness.</h1>
                <p>Benchmark resumes against job descriptions, identify gaps, generate recruiter-ready summaries, and export a polished report.</p>
            </div>
            <div class="hero-status">
                <span>{status}</span>
                <strong>ResumeIQ</strong>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="ResumeIQ | AI Resume Analyzer", page_icon="AI", layout="wide")
    init_session_state()
    load_css()

    resume_file, jd_file, jd_text, page = render_sidebar()
    build_analysis(resume_file, jd_file, jd_text)

    analyzer = GeminiAnalyzer()
    render_hero(st.session_state.analysis_result is not None)

    if not resume_file:
        st.markdown(
            """
            <div class="empty-state">
                <h3>Start a new analysis</h3>
                <p>Upload a resume PDF and add a job description from the sidebar. The dashboard will unlock ATS scoring, skill intelligence, GenAI analysis, and a downloadable report.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if not st.session_state.jd_text:
        st.info("Resume parsed successfully. Add a job description to calculate match score, ATS score, and AI recommendations.")
        with st.expander("Extracted Resume Text"):
            st.text_area("Resume text", st.session_state.resume_text, height=320, label_visibility="collapsed")
        return

    if page == "Dashboard":
        render_dashboard(st.session_state.analysis_result, analyzer)
    elif page == "Interview Questions":
        render_interview_questions(st.session_state.analysis_result, analyzer)
    elif page == "Learning Roadmap":
        render_learning_roadmap(st.session_state.analysis_result, analyzer)
    else:
        render_recruiter_summary(st.session_state.analysis_result, analyzer)

if __name__ == "__main__":
    main()