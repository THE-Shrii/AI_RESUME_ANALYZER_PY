import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.report_generator import ReportGenerator


def metric_card(title: str, value: str, subtitle: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{accent}">
            <span>{title}</span>
            <strong>{value}</strong>
            <small>{subtitle}</small>
            <div class="metric-glow"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tag_cloud(title: str, skills: list[str], tone: str) -> None:
    st.markdown(f"<h3 class='section-title'>{title}</h3>", unsafe_allow_html=True)
    if not skills:
        st.markdown("<p class='muted'>No skills detected in this group.</p>", unsafe_allow_html=True)
        return
    tags = "".join(f"<span class='tag {tone}'>{skill}</span>" for skill in skills)
    st.markdown(f"<div class='tag-cloud'>{tags}</div>", unsafe_allow_html=True)


def render_dashboard(result, analyzer) -> None:
    st.markdown("<div class='section-head'><h2>ATS Score Dashboard</h2><p>Live scoring across keyword match, resume structure, impact signals, and readiness.</p></div>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("ATS Score", f"{result.ats_breakdown.total}/100", "Recruiter screen readiness", "#22c55e")
    with col2:
        metric_card("Match Score", f"{result.match_score}%", "JD skill coverage", "#38bdf8")
    with col3:
        metric_card("Resume Strength", f"{result.resume_strength}/100", "Overall portfolio signal", "#a78bfa")
    with col4:
        metric_card("Interview Ready", f"{result.interview_readiness}/100", "Screening confidence", "#f59e0b")

    st.markdown(
        f"""
        <div class="glass-panel">
            <div class="meter-row"><span>Resume Strength Meter</span><strong>{result.resume_strength}%</strong></div>
            <div class="progress-shell"><div class="progress-fill" style="width:{result.resume_strength}%"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_col, radar_col = st.columns([1.05, 1])
    with chart_col:
        skill_df = pd.DataFrame(
            {"Status": ["Matched Skills", "Missing Skills"], "Count": [len(result.matched_skills), len(result.missing_skills)]}
        )
        fig = px.pie(skill_df, names="Status", values="Count", hole=0.55, color_discrete_sequence=["#22c55e", "#fb7185"])
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=360)
        st.plotly_chart(fig, use_container_width=True)

    with radar_col:
        breakdown = result.ats_breakdown.as_dict()
        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=list(breakdown.values()),
                theta=list(breakdown.keys()),
                fill="toself",
                line_color="#38bdf8",
                name="ATS",
            )
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 40])),
            height=360,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    heat_df = pd.DataFrame(
        {
            "Skill": result.jd_skills or ["No JD skills"],
            "Coverage": [100 if skill in result.matched_skills else 25 for skill in (result.jd_skills or ["No JD skills"])],
            "Type": ["Matched" if skill in result.matched_skills else "Missing" for skill in (result.jd_skills or ["No JD skills"])],
        }
    )
    heat = px.bar(heat_df, x="Skill", y="Coverage", color="Type", color_discrete_map={"Matched": "#22c55e", "Missing": "#fb7185"})
    heat.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=330)
    st.plotly_chart(heat, use_container_width=True)

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        tag_cloud("Matched Skills", result.matched_skills, "success")
    with col_b:
        tag_cloud("Missing Skills", result.missing_skills, "danger")
    with col_c:
        tag_cloud("Recommended Skills", result.recommended_skills, "info")
    with col_d:
        tag_cloud("Emerging Skills", result.emerging_skills, "warning")

    st.markdown("<div class='section-head'><h2>AI Resume Analysis</h2><p>Strengths, weaknesses, summary, suggestions, and improvement rewrites.</p></div>", unsafe_allow_html=True)
    if st.button("Generate AI Analysis", type="primary"):
        with st.spinner("Generating GenAI resume analysis..."):
            st.session_state.ai_analysis = analyzer.resume_analysis(result)
    if not st.session_state.ai_analysis:
        st.session_state.ai_analysis = analyzer.resume_analysis(result)
    st.markdown(f"<div class='ai-output'>{st.session_state.ai_analysis}</div>", unsafe_allow_html=True)

    st.markdown("<h3 class='section-title'>Resume Improvement Suggestions</h3>", unsafe_allow_html=True)
    for item in result.improvements:
        st.markdown(
            f"""
            <div class="before-after">
                <div><span>Before</span><p>{item['before']}</p></div>
                <div><span>After</span><p>{item['after']}</p></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("Prepare PDF Report"):
        if not st.session_state.interview_questions:
            st.session_state.interview_questions = analyzer.interview_questions(result)
        if not st.session_state.learning_roadmap:
            st.session_state.learning_roadmap = analyzer.learning_roadmap(result)
        if not st.session_state.recruiter_summary:
            st.session_state.recruiter_summary = analyzer.recruiter_summary(result)

    report_bytes = ReportGenerator().build_download_bytes(
        result,
        st.session_state.ai_analysis,
        st.session_state.interview_questions,
        st.session_state.learning_roadmap,
        st.session_state.recruiter_summary,
    )
    st.download_button("Download Professional Report", report_bytes, "resumeiq-ai-report.pdf", mime="application/pdf")

    with st.expander("Extracted Resume Text"):
        st.text_area("Resume text", result.resume_text, height=260, label_visibility="collapsed")
