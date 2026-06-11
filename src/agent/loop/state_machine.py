"""
Agent state machine
"""

from enum import Enum


class AgentState(Enum):
    RETRIEVE = "retrieve"
    REASON = "reason"
    REFLECT = "reflect"
    RESPOND = "respond"


class AgentStateMachine:
    """
    RETRIEVE → REASON → REFLECT → RESPOND
    """

    def __init__(
        self,
        retriever,
        llm,
        reflector
    ):
        self.retriever = retriever
        self.llm = llm
        self.reflector = reflector

    async def run(
        self,
        query: str
    ) -> str:

        state = AgentState.RETRIEVE

        context = None
        draft_answer = None
        final_answer = None

        while True:

            if state == AgentState.RETRIEVE:

                context = await self.retriever.retrieve(
                    query
                )

                state = AgentState.REASON

            elif state == AgentState.REASON:

                draft_answer = await self.llm.generate(
                    query=query,
                    context=context
                )

                state = AgentState.REFLECT

            elif state == AgentState.REFLECT:

                reflection = (
                    await self.reflector.review(
                        query=query,
                        answer=draft_answer,
                        context=context
                    )
                )

                if reflection["approved"]:
                    final_answer = draft_answer
                    state = AgentState.RESPOND

                else:
                    draft_answer = (
                        reflection["improved_answer"]
                    )

                    final_answer = draft_answer
                    state = AgentState.RESPOND

            elif state == AgentState.RESPOND:

                return final_answer