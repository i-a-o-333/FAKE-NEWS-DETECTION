import re
from collections import Counter
from typing import List


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", normalize_text(text))
    return [s.strip() for s in sentences if s.strip()]


def extract_topic(text: str) -> str:
    clean = normalize_text(text.lower())

    if "?" in clean:
        q = clean.split("?")[0]
        q = re.sub(r"^(is|are|do|does|did|can|could|should|would|will|what|why|how|when|where|who)\s+", "", q)
        return q[:100].strip() or "general topic"

    tokens = re.findall(r"[a-zA-Z][a-zA-Z\-']+", clean)
    stop = {
        "the", "a", "an", "and", "or", "to", "for", "from", "with", "that", "this", "have", "has", "had",
        "were", "was", "are", "is", "been", "being", "into", "about", "while", "when", "where", "which", "who",
        "what", "why", "how", "would", "could", "should", "said", "says", "according", "reported", "report", "news",
    }

    candidates = [t for t in tokens if len(t) > 3 and t not in stop]
    if not candidates:
        return "general topic"

    top = [w for w, _ in Counter(candidates).most_common(5)]
    return " ".join(top)


def extract_claim_candidates(text: str) -> List[str]:
    sentences = split_sentences(text)
    claims: List[str] = []

    assertion_patterns = [
        r"\b(is|are|was|were|has|have|had|will|confirmed|announced|revealed|caused|leads to|proves|demonstrates)\b",
        r"\b(according to|data shows|study finds|officials said|sources said)\b",
    ]

    for sentence in sentences:
        if len(sentence.split()) < 4:
            continue

        is_question = sentence.endswith("?")
        matched = any(re.search(pattern, sentence, re.IGNORECASE) for pattern in assertion_patterns)

        if matched and not is_question:
            claims.append(sentence)

    if not claims and text.strip():
        claims = [normalize_text(text)]

    return claims[:15]


def classify_claim_type(claim: str) -> str:
    c = claim.lower()
    if re.search(r"\b(will|expected|forecast|predict|likely to)\b", c):
        return "Predictive"
    if re.search(r"\b(should|must|need to|ought to)\b", c):
        return "Normative"
    if re.search(r"\b(according to|study|data|report|official|document|records)\b", c):
        return "Evidence-backed factual"
    return "Factual assertion"
