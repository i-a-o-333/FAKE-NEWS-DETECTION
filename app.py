import json
import re
import textwrap
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List

import streamlit as st


@dataclass
class ClaimAssessment:
    claim: str
    specific_or_vague: str
    evidence_provided: str
    independently_verifiable: str
    rationale: str


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text)
    return [c.strip() for c in chunks if c.strip()]


def extract_topic(text: str) -> str:
    cleaned = normalize_text(text.lower())
    if "?" in cleaned:
        q = cleaned.split("?")[0]
        q = re.sub(r"^(is|are|do|does|did|can|could|should|would|will|what|why|how|when|where|who)\s+", "", q)
        return q.strip()[:80] or "general topic"

    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-']+", cleaned)
    stop = {
        "the", "and", "that", "this", "with", "from", "they", "were", "have", "has",
        "had", "about", "would", "could", "should", "their", "there", "which", "into",
        "while", "where", "when", "what", "will", "been", "being", "then", "than", "because",
        "said", "says", "according", "report", "reported", "news"
    }
    content = [t for t in tokens if len(t) > 3 and t not in stop]
    if not content:
        return "general topic"
    common = [w for w, _ in Counter(content).most_common(4)]
    return " ".join(common)


def extract_claims(text: str) -> List[str]:
    sentences = split_sentences(text)
    claims = []
    claim_markers = re.compile(
        r"\b(is|are|was|were|will|has|have|had|confirmed|proved|shows|demonstrates|caused|leads|announced|revealed)\b",
        re.IGNORECASE,
    )
    for s in sentences:
        if len(s.split()) < 4:
            continue
        if claim_markers.search(s) or not s.endswith("?"):
            claims.append(s)
    if not claims and text.strip():
        claims = [text.strip()]
    return claims[:10]


def assess_claim_verifiability(claim: str) -> ClaimAssessment:
    claim_l = claim.lower()
    vague_markers = ["many", "some", "people say", "experts say", "obviously", "huge", "massive"]
    specific_markers = ["on", "in", "at", "according to", "study", "report", "data", "percent", "%", "202"]

    specificity = "Specific" if any(m in claim_l for m in specific_markers) or re.search(r"\d", claim_l) else "Vague"
    evidence = "Referenced" if any(m in claim_l for m in ["according to", "study", "data", "report", "source"]) else "Not explicit"

    if specificity == "Specific" and evidence == "Referenced":
        verifiable = "High"
    elif specificity == "Specific":
        verifiable = "Medium"
    else:
        verifiable = "Low"

    if any(m in claim_l for m in vague_markers):
        specificity = "Vague"
        if verifiable == "High":
            verifiable = "Medium"

    rationale = (
        f"The claim is assessed as {specificity.lower()} because it "
        f"{'includes concrete anchors (time/place/data)' if specificity == 'Specific' else 'lacks concrete anchors'}. "
        f"Evidence is {evidence.lower()}, so independent checking potential is {verifiable.lower()}."
    )

    return ClaimAssessment(
        claim=claim,
        specific_or_vague=specificity,
        evidence_provided=evidence,
        independently_verifiable=verifiable,
        rationale=rationale,
    )


def infer_intent(text: str) -> Dict[str, str]:
    t = text.lower()
    persuasive_cues = ["must", "everyone", "undeniable", "share this", "act now", "wake up"]
    political_cues = ["election", "government", "party", "policy", "senate", "president"]
    emotional_cues = ["shocking", "outrage", "fear", "betrayal", "threat", "disaster"]
    pr_cues = ["innovation", "leading", "world-class", "award-winning", "trusted brand"]

    if any(c in t for c in pr_cues):
        label = "Reputation improvement (PR)"
        reason = "Language highlights image-building and positive brand framing."
    elif any(c in t for c in political_cues):
        label = "Political influence"
        reason = "Content focuses on political actors/policy outcomes and likely persuasion around public opinion."
    elif any(c in t for c in persuasive_cues):
        label = "Persuasion"
        reason = "Direct imperative language suggests the author is trying to shape reader behavior or belief."
    elif any(c in t for c in emotional_cues):
        label = "Emotional manipulation"
        reason = "Emotionally loaded framing dominates over calm informational framing."
    else:
        label = "Neutral information"
        reason = "Tone appears primarily descriptive without strong persuasion markers."
    return {"intent": label, "reason": reason}


def detect_manipulation_patterns(text: str) -> List[str]:
    t = text.lower()
    findings = []
    if re.search(r"\b(always|never|everyone|no one|all of them)\b", t):
        findings.append("One-sided framing: absolute language suggests overgeneralization.")
    if re.search(r"\b(hero|villain|evil|savior|traitor)\b", t):
        findings.append("Hero/villain narrative detected: moral binary framing may reduce nuance.")
    if re.search(r"\b(shocking|terrifying|you won't believe|outrage)\b", t):
        findings.append("Emotional pressure detected: heightened emotional cues may override evidence-based reasoning.")
    if "according to" not in t and "source" not in t and "data" not in t:
        findings.append("Unsupported assertions risk: limited visible sourcing language in the input.")
    return findings or ["No strong manipulation pattern detected from text alone; external source validation still required."]


def compute_scores(assessments: List[ClaimAssessment], manip_findings: List[str], intent: str) -> Dict[str, int]:
    total = max(len(assessments), 1)
    high = sum(1 for a in assessments if a.independently_verifiable == "High")
    med = sum(1 for a in assessments if a.independently_verifiable == "Medium")

    reliability = int((high * 1.0 + med * 0.65) / total * 100)
    objectivity = int(max(5, 100 - (len(manip_findings) - 1) * 15 - (20 if intent in {"Persuasion", "Emotional manipulation"} else 0)))
    propaganda_prob = int(min(95, (100 - objectivity) * 0.7 + (30 if intent in {"Political influence", "Reputation improvement (PR)"} else 10)))

    return {
        "objectivity": max(0, min(100, objectivity)),
        "reliability": max(0, min(100, reliability)),
        "propaganda": max(0, min(100, propaganda_prob)),
    }


def classify_final_assessment(scores: Dict[str, int], intent_label: str) -> str:
    if scores["reliability"] >= 70 and scores["objectivity"] >= 65:
        return "Likely factual reporting"
    if intent_label == "Reputation improvement (PR)" or scores["propaganda"] >= 70:
        return "Likely PR or reputation management"
    if intent_label == "Political influence" and scores["propaganda"] >= 60:
        return "Likely propaganda"
    return "Likely misleading or unreliable"


def fetch_wikipedia_refs(topic: str) -> List[Dict[str, str]]:
    query = urllib.parse.quote(topic)
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&format=json&srlimit=4"
    refs = []
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "Unknown")
            snippet = re.sub(r"<.*?>", "", item.get("snippet", "")).replace("&quot;", '"')
            refs.append({
                "title": title,
                "source": "Wikipedia (encyclopedic mainstream reference)",
                "summary": snippet,
                "link": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                "viewpoint": "Mainstream/reference"
            })
    except Exception:
        pass
    return refs


def fetch_crossref_refs(topic: str) -> List[Dict[str, str]]:
    query = urllib.parse.quote(topic)
    url = f"https://api.crossref.org/works?query.title={query}&rows=3"
    refs = []
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for item in data.get("message", {}).get("items", [])[:3]:
            title = (item.get("title") or ["Untitled"])[0]
            source = (item.get("container-title") or ["Scholarly publication"])[0]
            doi = item.get("DOI", "")
            link = f"https://doi.org/{doi}" if doi else ""
            refs.append({
                "title": title,
                "source": source,
                "summary": "Scholarly/technical source that can be used to validate or challenge claims.",
                "link": link,
                "viewpoint": "Academic/independent"
            })
    except Exception:
        pass
    return refs


def generate_alt_view_refs(topic: str) -> List[Dict[str, str]]:
    return [
        {
            "title": f"Alternative analysis threads on '{topic}'",
            "source": "Independent newsletters / blogs",
            "summary": "Look for argument quality, source transparency, and direct evidence citations before trusting conclusions.",
            "link": "",
            "viewpoint": "Alternative viewpoint",
        },
        {
            "title": f"Open-source intelligence discussions: {topic}",
            "source": "OSINT communities",
            "summary": "Useful for triangulating geolocation, timeline reconstruction, and primary-source media verification.",
            "link": "",
            "viewpoint": "Obscure/OSINT",
        },
    ]


def find_reference_articles(topic: str) -> List[Dict[str, str]]:
    refs = fetch_wikipedia_refs(topic) + fetch_crossref_refs(topic)
    refs += generate_alt_view_refs(topic)
    dedup = []
    seen = set()
    for r in refs:
        key = (r["title"].lower(), r["source"].lower())
        if key not in seen:
            seen.add(key)
            dedup.append(r)
    return dedup[:10]


def build_follow_up_questions(topic: str, claims: List[str], manip_findings: List[str]) -> List[str]:
    questions = [
        "What direct evidence supports each claim (documents, datasets, official records, or firsthand media)?",
        "Which independent sources confirm or contradict the same events?",
        "Who benefits if this narrative is widely believed, and what incentives are present?",
        "Are there timeline inconsistencies or missing context that could change interpretation?",
        "Can any claim be falsified with publicly available data?",
    ]
    if claims:
        questions.append(f"Which claim about '{topic}' is most testable first, and what is the best verification method?")
    if len(manip_findings) > 1:
        questions.append("Which parts of the text rely on emotion or framing rather than verifiable facts?")
    return questions


def score_color(score: int, inverse: bool = False) -> str:
    if inverse:
        score = 100 - score
    if score >= 70:
        return "#1f9d55"
    if score >= 40:
        return "#d9a404"
    return "#d64545"


def render_score(label: str, score: int, inverse: bool = False):
    color = score_color(score, inverse=inverse)
    st.markdown(f"**{label}: {score}/100**")
    st.markdown(
        f"""
        <div style='background:#f0f0f0;border-radius:12px;overflow:hidden;height:18px;margin-bottom:12px;'>
            <div style='width:{score}%;background:{color};height:18px;transition:width 0.6s;'></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="News Intelligence Analyzer", layout="wide")

    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(160deg, #ff4d4d 0%, #ffe5e5 40%, #ffffff 100%);
        }
        .block-container {max-width: 1000px; padding-top: 2rem; padding-bottom: 3rem;}
        .main-title {text-align:center; font-size: 3rem; font-weight: 700; color: #5a0000;}
        .subtitle {text-align:center; font-size: 1.2rem; color:#7a1c1c; margin-bottom: 1rem;}
        .panel {
            background: rgba(255,255,255,0.86);
            border: 1px solid rgba(255,255,255,0.6);
            border-radius: 16px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 8px 30px rgba(130, 0, 0, 0.08);
        }
        .flower {
            position: fixed;
            top: -10%;
            z-index: 0;
            pointer-events: none;
            opacity: 0.55;
            animation-name: fall, sway;
            animation-timing-function: linear, ease-in-out;
            animation-iteration-count: infinite, infinite;
        }
        @keyframes fall {
            0% { transform: translateY(-10vh) rotate(0deg); }
            100% { transform: translateY(120vh) rotate(360deg); }
        }
        @keyframes sway {
            0%, 100% { margin-left: 0; }
            50% { margin-left: 40px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    flowers_html = ""
    for i in range(24):
        left = (i * 4.1) % 100
        delay = (i * 0.6) % 12
        duration = 10 + (i % 8)
        size = 16 + (i % 5) * 7
        flowers_html += f"<div class='flower' style='left:{left}%;font-size:{size}px;animation-duration:{duration}s,{duration/2}s;animation-delay:{delay}s,{delay/2}s;'>🌸</div>"
    st.markdown(flowers_html, unsafe_allow_html=True)

    st.markdown("<div class='main-title'>News Intelligence Analyzer</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>AI Narrative Investigation System</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    user_input = st.text_area(
        "Enter news text or an investigation question",
        height=220,
        placeholder="Example: Do aliens exist?\nOr paste a full article claim to investigate...",
    )
    analyze = st.button("🔎 Analyze", use_container_width=True, type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze and user_input.strip():
        cleaned = normalize_text(user_input)
        topic = extract_topic(cleaned)
        claims = extract_claims(cleaned)
        assessments = [assess_claim_verifiability(c) for c in claims]
        intent = infer_intent(cleaned)
        manip_findings = detect_manipulation_patterns(cleaned)
        scores = compute_scores(assessments, manip_findings, intent["intent"])
        refs = find_reference_articles(topic)
        followups = build_follow_up_questions(topic, claims, manip_findings)
        final_assessment = classify_final_assessment(scores, intent["intent"])

        st.markdown("## INTELLIGENCE REPORT")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("### SUMMARY")
            st.write(
                textwrap.fill(
                    f"Primary topic extracted: {topic}. The analysis identified {len(claims)} key claim(s), "
                    f"evaluated verifiability, assessed likely intent as '{intent['intent']}', and generated "
                    f"a reliability-centered intelligence judgment.",
                    width=110,
                )
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='panel'>", unsafe_allow_html=True)
            st.markdown("### SCORES")
            render_score("Objectivity Score", scores["objectivity"])
            render_score("Factual Reliability Score", scores["reliability"])
            render_score("PR / Propaganda Probability", scores["propaganda"], inverse=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### EXTRACTED CLAIMS")
        for i, a in enumerate(assessments, start=1):
            st.markdown(f"**Claim {i}:** {a.claim}")
            st.caption(
                f"Specificity: {a.specific_or_vague} | Evidence: {a.evidence_provided} | "
                f"Independent Verifiability: {a.independently_verifiable}"
            )
            st.write(a.rationale)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### REFERENCE FINDINGS")
        st.caption("Mainstream, academic, independent, and alternative viewpoints for triangulation.")
        for ref in refs:
            st.markdown(f"**{ref['title']}**  ")
            st.write(f"Source: {ref['source']} | Viewpoint: {ref['viewpoint']}")
            st.write(ref["summary"])
            if ref["link"]:
                st.markdown(f"[Open source link]({ref['link']})")
            st.divider()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### LIKELY INTENT")
        st.write(f"**{intent['intent']}**")
        st.write(intent["reason"])

        st.markdown("### MANIPULATION RISK")
        for f in manip_findings:
            st.write(f"- {f}")

        st.markdown("### FINAL ASSESSMENT")
        st.write(f"**{final_assessment}**")
        st.markdown("### REASONING")
        st.write(
            "Conclusion is derived from claim-level verifiability checks, sourcing cues, narrative framing, "
            "and triangulated reference context rather than simple keyword-based classification."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        st.markdown("### Further Investigation Questions")
        for q in followups:
            st.write(f"- {q}")
        st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
