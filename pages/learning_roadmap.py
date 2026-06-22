import streamlit as st


def render_learning_roadmap(result, analyzer) -> None:
    st.markdown("<div class='section-head'><h2>Learning Roadmap Generator</h2><p>A four-week learning sprint for missing and recommended skills.</p></div>", unsafe_allow_html=True)
    if st.button("Generate 4-Week Roadmap", type="primary") or not st.session_state.learning_roadmap:
        with st.spinner("Building roadmap..."):
            st.session_state.learning_roadmap = analyzer.learning_roadmap(result)
    st.markdown(f"<div class='ai-output'>{st.session_state.learning_roadmap}</div>", unsafe_allow_html=True)
