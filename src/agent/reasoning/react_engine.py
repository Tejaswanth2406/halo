"""
ReAct reasoning engine
"""

from typing import Dict


class ReActEngine:
    """
    ReAct framework:
    Thought → Action → Observation loop
    """

    MAX_STEPS = 3

    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    async def reason(
        self,
        query: str,
        context: str
    ) -> str:

        state = {
            "thought": "",
            "action": None,
            "observation": "",
            "final": ""
        }

        for step in range(self.MAX_STEPS):

            # 1. Thought
            thought = await self.llm.generate(
                f"""
You are a ReAct agent.

Question:
{query}

Context:
{context}

Think step-by-step.
What should you do next?
"""
            )

            state["thought"] = thought

            # 2. Action (decide tool use or final answer)
            action = await self.llm.generate(
                f"""
Based on this thought:
{thought}

Decide next action:
- search
- retrieve
- calculate
- finish

Return only one word.
"""
            )

            state["action"] = action.strip().lower()

            # 3. Execute Action
            if state["action"] == "retrieve":

                observation = await self.tools["retriever"].retrieve(
                    query
                )

            elif state["action"] == "search":

                observation = await self.tools["search"].search(
                    query
                )

            else:
                observation = "No tool used"

            state["observation"] = str(observation)

            # 4. Decide if finished
            final = await self.llm.generate(
                f"""
Thought:
{thought}

Observation:
{observation}

Should we finish? If yes, return final answer.
If not, say CONTINUE.
"""
            )

            if "continue" not in final.lower():
                state["final"] = final
                return final

        # fallback
        return state["final"] or "Unable to complete reasoning."