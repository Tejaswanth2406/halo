"""
Agent core entry point
"""

class Agent:
    """Top-level RAG agent."""

    def __init__(
        self,
        guardrails,
        planner,
        retriever_agent,
        synthesizer,
        critic,
        confidence_scorer,
        gap_detector,
        hallucination_detector,
        citation_formatter,
        response_generator
    ):
        self.guardrails = guardrails
        self.planner = planner
        self.retriever = retriever_agent
        self.synthesizer = synthesizer
        self.critic = critic
        self.confidence_scorer = confidence_scorer
        self.gap_detector = gap_detector
        self.hallucination_detector = hallucination_detector
        self.citation_formatter = citation_formatter
        self.response_generator = response_generator

    async def process_query(self, query: str) -> str:
        """Process query through full pipeline."""

        # 1. Input guardrails
        safe_query = await self.guardrails.validate_input(query)

        # 2. Planning
        plan = await self.planner.plan(safe_query)

        # 3. Retrieval (execute first task or full query)
        context = await self.retriever.retrieve(safe_query)

        # 4. Synthesis
        draft = await self.synthesizer.synthesize(context)

        # 5. Reflection layer
        critique = await self.critic.critique(draft, context)

        gaps = await self.gap_detector.detect_gaps(draft, context)

        hallucinations = await self.hallucination_detector.detect(
            draft,
            context
        )

        confidence = self.confidence_scorer.score(draft, context)

        # 6. Decision gate
        if (
            not critique.get("approved")
            or confidence < 0.6
            or gaps
            or hallucinations
        ):
            return (
                "I could not generate a fully "
                "reliable answer from the provided context."
            )

        # 7. Citation formatting
        cited = self.citation_formatter.format_citations(
            draft,
            context
        )

        # 8. Final response shaping
        final = await self.response_generator.generate(cited)

        # 9. Output guardrails (optional but recommended)
        safe_output = await self.guardrails.validate_output(final)

        return safe_output