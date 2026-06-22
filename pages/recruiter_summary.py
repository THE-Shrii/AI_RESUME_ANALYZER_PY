import streamlit as st


def render_recruiter_summary(result, analyzer) -> None:
    st.markdown("<div class='section-head'><h2>Recruiter Summary Generator</h2><p>Candidate overview, strengths, concerns, and hiring recommendation.</p></div>", unsafe_allow_html=True)
    if st.button("Generate Recruiter Summary", type="primary") or not st.session_state.recruiter_summary:
        with st.spinner("Writing recruiter summary..."):
            st.session_state.recruiter_summary = analyzer.recruiter_summary(result)
    st.markdown(f"<div class='ai-output'>{st.session_state.recruiter_summary}</div>", unsafe_allow_html=True)
