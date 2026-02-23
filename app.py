import streamlit as st

from src.news_intel.analyzer import analyze_text
from src.news_intel.text_processing import normalize_text
from src.news_intel.ui import inject_theme, render_report


def main() -> None:
    st.set_page_config(page_title="News Intelligence Analyzer", layout="wide")
    inject_theme()

    st.markdown("<div class='main-title'>News Intelligence Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI Narrative Investigation System</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    user_input = st.text_area(
        "Enter news text or an investigation question",
        height=240,
        placeholder="Paste news text or enter a topic/question such as: Do aliens exist?",
    )
    analyze_clicked = st.button("🔎 Analyze", use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_clicked and user_input.strip():
        result = analyze_text(normalize_text(user_input))
        render_report(result)


if __name__ == "__main__":
    main()
