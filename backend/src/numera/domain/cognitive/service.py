from numera.domain.cognitive.models import CognitiveDecision, CognitiveDecisionRequest


class CognitiveService:
    """First placeholder for the Numera Cognitive System.

    v0.1 does not implement real AI yet.
    It provides the stable interface that future engines will use:
    Understanding, Memory, Context, Rules, Reasoning, Confidence, Planning, Reflection.
    """

    def evaluate(self, request: CognitiveDecisionRequest) -> CognitiveDecision:
        if request.risk_level == "high":
            return CognitiveDecision(
                decision_id="decision_demo_001",
                status="requires_human_review",
                recommendation="Do not automate. Human approval required.",
                confidence=0.55,
                explanation=[
                    "High-risk action detected.",
                    "Numera must ask before acting.",
                    "Human approval is required by system principles.",
                ],
            )

        return CognitiveDecision(
            decision_id="decision_demo_001",
            status="recommendation_ready",
            recommendation="Proceed with low-risk recommendation.",
            confidence=0.82,
            explanation=[
                "Input was received and classified.",
                "No blocking rule detected in v0.1 placeholder.",
                "Future versions will use Memory, Context and Rule Engines.",
            ],
        )
