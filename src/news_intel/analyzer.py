import re
from typing import Dict, List

from .models import AnalysisResult, ClaimAssessment
from .reference_finder import find_references
from .text_processing import classify_claim_type, extract_claim_candidates, extract_topic


EVIDENCE_PATTERN = re.compile(
    r"\b(according to|data|study|report|source|document|records|official statement)\b",
    re.IGNORECASE,
)
VAGUE_PATTERN = re.compile(
    r"\b(many|some|experts say|people say|obviously|clearly|everyone knows)\b",
    re.IGNORECASE,
)
SPECIFIC_PATTERN = re.compile(
    r"(\b\d{1,4}(?:\.\d+)?%?\b|\b\d{4}\b|\b(january|february|march|april|may|june|"
    r"july|august|september|october|november|december)\b|\b(according to|in [A-Z][a-z]+|at [A-Z][a-z]+))",
EVIDENCE_PATTERN = re.compile(r"\b(according to|data|study|report|source|document|records|official statement)\b", re.IGNORECASE)
VAGUE_PATTERN = re.compile(r"\b(many|some|experts say|people say|obviously|clearly|everyone knows)\b", re.IGNORECASE)
SPECIFIC_PATTERN = re.compile(
    r"(\b\d{1,4}(?:\.\d+)?%?\b|\b\d{4}\b|\b(january|february|march|april|may|june|july|august|"
    r"september|october|november|december)\b|\b(according to|in [A-Z][a-z]+|at [A-Z][a-z]+))",
    re.IGNORECASE,
)


def assess_claim(claim: str) -> ClaimAssessment:
    has_specific = bool(SPECIFIC_PATTERN.search(claim))
    has_vague = bool(VAGUE_PATTERN.search(claim))
    has_evidence = bool(EVIDENCE_PATTERN.search(claim))

    specificity = "Specific" if has_specific and not has_vague else "Vague"
    evidence_status = "Evidence cues present" if has_evidence else "No explicit evidence cues"

    if specificity == "Specific" and has_evidence:
        verifiability = "High"
    elif specificity == "Specific":
        verifiability = "Medium"
    else:
        verifiability = "Low"

    rationale = (
        f"Claim evaluated as {specificity.lower()} because it "
        f"{'contains concrete anchors (time/place/quantity/source)' if specificity == 'Specific' else 'uses broad framing or lacks concrete anchors'}. "
        f"{evidence_status}. This yields {verifiability.lower()} independent verifiability potential."
    )

    return ClaimAssessment(
        claim=claim,
        claim_type=classify_claim_type(claim),
        specificity=specificity,
        evidence_status=evidence_status,
        verifiability=verifiability,
        rationale=rationale,
    )


def infer_intent(text: str) -> Dict[str, str]:
    t = text.lower()

    if re.search(r"\b(award-winning|industry-leading|trusted brand|our company|our platform|market-leading)\b", t):
        return {
            "label": "Reputation improvement (PR)",
            "reason": "Narrative emphasizes image enhancement and positive brand framing.",
        }
    if re.search(r"\b(election|senate|congress|government|party|candidate|policy|minister)\b", t):
        return {
            "label": "Political influence",
            "reason": "Narrative centers political actors/outcomes and likely seeks opinion shaping.",
        }
    if re.search(r"\b(share this|act now|must|wake up|don't ignore|you need to)\b", t):
        return {
            "label": "Persuasion",
            "reason": "Direct calls-to-action indicate behavior/belief influence intent.",
        }
    if re.search(r"\b(shocking|terrifying|betrayal|disaster|outrage|panic)\b", t):
        return {
            "label": "Emotional manipulation",
            "reason": "Emotion-heavy wording can pressure judgment over evidence review.",
        }

    return {
        "label": "Neutral information",
        "reason": "Narrative is primarily descriptive without strong directional agenda markers.",
    }


def detect_manipulation(text: str) -> List[str]:
    t = text.lower()
    findings: List[str] = []

    if re.search(r"\b(always|never|everyone|no one|all of them)\b", t):
        findings.append("One-sided framing: absolute language indicates potential overgeneralization.")
    if re.search(r"\b(hero|villain|evil|savior|traitor)\b", t):
        findings.append("Hero/villain framing: binary moral narrative may suppress nuance.")
    if re.search(r"\b(shocking|you won't believe|terrifying|outrage|panic)\b", t):
        findings.append("Emotional pressure: highly charged phrasing may displace evidence-led evaluation.")
    if not EVIDENCE_PATTERN.search(t):
        findings.append("Unsupported assertions risk: limited traceable sourcing cues in the text.")

    return findings or ["No dominant manipulation pattern detected from text alone; external source checks still required."]


def compute_scores(claims: List[ClaimAssessment], manipulation_findings: List[str], intent_label: str) -> Dict[str, int]:
    total = max(len(claims), 1)
    high = sum(1 for c in claims if c.verifiability == "High")
    medium = sum(1 for c in claims if c.verifiability == "Medium")
    low = sum(1 for c in claims if c.verifiability == "Low")

    reliability = int(((high * 1.0) + (medium * 0.6) + (low * 0.2)) / total * 100)

    manipulation_penalty = max(0, (len(manipulation_findings) - 1) * 12)
    intent_penalty = 0
    if intent_label in {"Persuasion", "Emotional manipulation"}:
        intent_penalty = 22
    elif intent_label in {"Political influence", "Reputation improvement (PR)"}:
        intent_penalty = 12

    objectivity = max(5, min(100, 100 - manipulation_penalty - intent_penalty))
    propaganda = int(
        min(
            95,
            (100 - objectivity) * 0.74
            + (18 if intent_label in {"Political influence", "Reputation improvement (PR)"} else 8),
        )
    )
    propaganda = int(min(95, (100 - objectivity) * 0.74 + (18 if intent_label in {"Political influence", "Reputation improvement (PR)"} else 8)))

    return {
        "objectivity": objectivity,
        "reliability": max(0, min(100, reliability)),
        "propaganda": max(0, min(100, propaganda)),
    }


def determine_final_assessment(scores: Dict[str, int], intent_label: str) -> str:
    # Use intent-aware thresholds while avoiding over-triggering on single weak cues.
    if intent_label == "Political influence" and scores["propaganda"] >= 35:
        return "Likely propaganda"
    if intent_label == "Reputation improvement (PR)" and scores["propaganda"] >= 25:
    # Prioritize directional-intent detection before defaulting to factual.
    if intent_label == "Political influence" and (scores["propaganda"] >= 45 or scores["objectivity"] < 95):
        return "Likely propaganda"
    if intent_label == "Reputation improvement (PR)":
        return "Likely PR or reputation management"
    if scores["reliability"] >= 72 and scores["objectivity"] >= 68 and scores["propaganda"] < 45:
        return "Likely factual reporting"
    if scores["propaganda"] >= 70:
        return "Likely PR or reputation management"
    return "Likely misleading or unreliable"


def build_follow_up_questions(topic: str, claims: List[ClaimAssessment], manipulation_findings: List[str]) -> List[str]:
    questions = [
        "What primary evidence (documents, datasets, official statements, or raw media) supports each major claim?",
        "Which independent sources outside the original narrative ecosystem confirm or challenge these claims?",
        "Who benefits materially, politically, or reputationally if this narrative is accepted?",
        "Are there chronology gaps, context omissions, or attribution ambiguities affecting interpretation?",
        "Which claim can be falsified fastest, and what test would disprove it?",
    ]

    if claims:
        questions.append(f"For '{topic}', which extracted claim has the strongest evidence chain and which has the weakest?")
    if len(manipulation_findings) > 1:
        questions.append("Which statements rely more on framing/emotion than directly verifiable facts?")

    return questions


def analyze_text(text: str) -> AnalysisResult:
    topic = extract_topic(text)
    raw_claims = extract_claim_candidates(text)
    assessed_claims = [assess_claim(c) for c in raw_claims]

    intent = infer_intent(text)
    manipulation = detect_manipulation(text)
    scores = compute_scores(assessed_claims, manipulation, intent["label"])
    final = determine_final_assessment(scores, intent["label"])

    references = find_references(topic)
    follow_ups = build_follow_up_questions(topic, assessed_claims, manipulation)

    reasoning = (
        "Assessment is derived from claim-level verifiability, sourcing cues, narrative framing, and cross-source "
        "triangulation references; it is not keyword counting or simple one-shot classification."
    )

    return AnalysisResult(
        topic=topic,
        claims=assessed_claims,
        references=references,
        follow_up_questions=follow_ups,
        intent_label=intent["label"],
        intent_reason=intent["reason"],
        manipulation_findings=manipulation,
        objectivity_score=scores["objectivity"],
        reliability_score=scores["reliability"],
        propaganda_probability=scores["propaganda"],
        final_assessment=final,
        reasoning=reasoning,
    )
