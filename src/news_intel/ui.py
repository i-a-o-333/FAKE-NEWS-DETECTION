import streamlit as st

from .models import AnalysisResult


def score_color(score: int, inverse: bool = False) -> str:
    effective = (100 - score) if inverse else score
    if effective >= 70:
        return "#18b65e"
    if effective >= 40:
        return "#ffc107"
    return "#ff3b30"


def render_score(label: str, score: int, inverse: bool = False) -> None:
    color = score_color(score, inverse=inverse)
    st.markdown(f"**{label}: {score}/100**")
    st.markdown(
        f"""
        <div style='background:#f2f2f2;border-radius:999px;overflow:hidden;height:18px;margin-bottom:12px;'>
            <div style='width:{score}%;background:{color};height:18px;transition:width .5s ease;'></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at 15% 20%, #ff1e1e 0%, #ff4545 28%, #ff7f7f 55%, #ffd5d5 78%, #ffffff 100%);
        }
        .block-container {
            max-width: 1120px;
            padding-top: 1.4rem;
            padding-bottom: 2.8rem;
        }
        .main-title {
            text-align:center; font-size: 3.3rem; font-weight: 900;
            color: #4d0000; text-shadow: 0 3px 14px rgba(255,255,255,.45);
            letter-spacing: .6px;
        }
        .subtitle {
            text-align:center; font-size: 1.2rem; color: #7a0e0e;
            margin-bottom: 1rem; font-weight: 650;
        }
        .panel {
            background: linear-gradient(180deg, rgba(255,255,255,.94), rgba(255,255,255,.86));
            border: 1px solid rgba(255,255,255,0.68);
            border-radius: 20px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 34px rgba(110,0,0,.16);
            backdrop-filter: blur(2px);
        }
        .flower {
            position: fixed;
            top: -12%;
            z-index: 0;
            pointer-events: none;
            opacity: 0.70;
            animation-name: fall, dance;
            animation-timing-function: linear, ease-in-out;
            animation-iteration-count: infinite, infinite;
            filter: saturate(1.5);
        }
        @keyframes fall {
            0% { transform: translateY(-10vh) rotate(0deg); }
            100% { transform: translateY(120vh) rotate(360deg); }
        }
        @keyframes dance {
            0%, 100% { margin-left: 0; }
            50% { margin-left: 52px; }
        }
        .kpi {
            border-radius: 14px;
            padding: .65rem .85rem;
            border: 1px solid rgba(0,0,0,.08);
            background: rgba(255,255,255,.84);
            margin-bottom: .6rem;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.8);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    flowers = ""
    for i in range(40):
        left = (i * 2.5) % 100
        delay = (i * 0.33) % 10
        duration = 8 + (i % 9)
        size = 14 + (i % 7) * 6
        flowers += (
            f"<div class='flower' style='left:{left}%;font-size:{size}px;"
            f"animation-duration:{duration}s,{duration/2.0}s;animation-delay:{delay}s,{delay/2}s;'>🌸</div>"
        )
    st.markdown(flowers, unsafe_allow_html=True)


def _risk_label(score: int, inverse: bool = False) -> str:
    value = 100 - score if inverse else score
    if value >= 70:
        return "Low Risk"
    if value >= 40:
        return "Medium Risk"
    return "High Risk"


def render_report(result: AnalysisResult) -> None:
    st.markdown("## INTELLIGENCE REPORT")

    col_a, col_b = st.columns([1.25, 1])
    with col_a:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### SUMMARY")
        st.write(
            f"Topic extracted: **{result.topic}**. The system extracted **{len(result.claims)}** claim(s), "
            f"evaluated verifiability and narrative intent, then produced an intelligence-style assessment."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### SCOREBOARD")
        render_score("Objectivity Score", result.objectivity_score)
        render_score("Factual Reliability Score", result.reliability_score)
        render_score("PR / Propaganda Probability", result.propaganda_probability, inverse=True)
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='kpi'><strong>Objectivity Risk:</strong> {_risk_label(result.objectivity_score)}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi'><strong>Reliability Risk:</strong> {_risk_label(result.reliability_score)}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi'><strong>PR/Propaganda Risk:</strong> {_risk_label(result.propaganda_probability, inverse=True)}</div>", unsafe_allow_html=True)

    tab_claims, tab_refs, tab_analysis, tab_questions = st.tabs([
        "Extracted Claims",
        "Reference Findings",
        "Intent & Manipulation",
        "Further Questions",
    ])

    with tab_claims:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### EXTRACTED CLAIMS")
        for idx, claim in enumerate(result.claims, start=1):
            st.markdown(f"**Claim {idx}:** {claim.claim}")
            st.caption(
                f"Type: {claim.claim_type} | Specificity: {claim.specificity} | "
                f"Evidence: {claim.evidence_status} | Verifiability: {claim.verifiability}"
            )
            st.write(claim.rationale)
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_refs:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### REFERENCE FINDINGS")
        st.caption("Mainstream, non-mainstream, obscure, and alternative viewpoints for triangulation.")
        for ref in result.references:
            st.markdown(f"**{ref.title}**")
            st.write(f"Source: {ref.source} | Viewpoint: {ref.viewpoint}")
            st.write(ref.summary)
            if ref.link:
                st.markdown(f"[Open source link]({ref.link})")
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_analysis:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### LIKELY INTENT")
        st.write(f"**{result.intent_label}**")
        st.write(result.intent_reason)

        st.markdown("### MANIPULATION RISK")
        for finding in result.manipulation_findings:
            st.write(f"- {finding}")

        st.markdown("### FINAL ASSESSMENT")
        st.write(f"**{result.final_assessment}**")

        st.markdown("### REASONING")
        st.write(result.reasoning)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_questions:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### Further Investigation Questions")
        for question in result.follow_up_questions:
            st.write(f"- {question}")
        st.markdown("</div>", unsafe_allow_html=True)
