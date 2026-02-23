from dataclasses import dataclass
from typing import List


@dataclass
class ClaimAssessment:
    claim: str
    claim_type: str
    specificity: str
    evidence_status: str
    verifiability: str
    rationale: str


@dataclass
class ReferenceArticle:
    title: str
    source: str
    summary: str
    link: str
    viewpoint: str


@dataclass
class AnalysisResult:
    topic: str
    claims: List[ClaimAssessment]
    references: List[ReferenceArticle]
    follow_up_questions: List[str]
    intent_label: str
    intent_reason: str
    manipulation_findings: List[str]
    objectivity_score: int
    reliability_score: int
    propaganda_probability: int
    final_assessment: str
    reasoning: str
