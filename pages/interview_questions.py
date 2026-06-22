import streamlit as st


def render_interview_questions(result, analyzer) -> None:
    st.markdown("<div class='section-head'><h2>AI Interview Question Generator</h2><p>Questions are tailored to the resume, JD, matched skills, and skill gaps.</p></div>", unsafe_allow_html=True)
    if st.button("Generate Interview Questions", type="primary") or not st.session_state.interview_questions:
        with st.spinner("Generating interview questions..."):
            st.session_state.interview_questions = analyzer.interview_questions(result)
    st.markdown(f"<div class='ai-output'>{st.session_state.interview_questions}</div>", unsafe_allow_html=True)
