import streamlit as st

from src.news_intel.analyzer import analyze_text
from src.news_intel.text_processing import normalize_text
from src.news_intel.ui import inject_theme, render_report


def main() -> None:
    st.set_page_config(page_title="News Intelligence Analyzer", layout="wide", page_icon="🧠")
    inject_theme()

    st.markdown("<div class='main-title'>News Intelligence Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI Narrative Investigation System</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("#### Input")
    user_input = st.text_area(
        "Enter news text or an investigation question",
        height=240,
        placeholder=(
            "Paste news text or enter a question such as: \n"
            "Do aliens exist?\n"
            "Did policy X reduce inflation in 2023?"
        ),
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        analyze_clicked = st.button("🔎 Analyze", use_container_width=True, type="primary")
    with c2:
        clear_clicked = st.button("🧹 Clear", use_container_width=True)

    if clear_clicked:
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_clicked:
        if not user_input.strip():
            st.warning("Please enter news text or a topic/question before clicking Analyze.")
            return

        with st.spinner("Investigating claims, references, and narrative signals..."):
            result = analyze_text(normalize_text(user_input))

        render_report(result)


if __name__ == "__main__":
    main()
