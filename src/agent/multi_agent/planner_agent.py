"""
Planner agent for task decomposition
"""

import re


class PlannerAgent:
    """Decompose tasks into sub-tasks."""

    async def plan(
        self,
        query: str
    ) -> list:
        """
        Create a task plan.
        """

        query = query.strip()

        tasks = []

        # Comparison queries
        if re.search(
            r"\b(compare|difference|versus|vs)\b",
            query.lower()
        ):
            tasks.extend([
                "Retrieve information for entity A",
                "Retrieve information for entity B",
                "Compare findings",
                "Generate final answer"
            ])

        # Multi-part questions
        elif " and " in query.lower():

            parts = [
                p.strip()
                for p in query.split(" and ")
                if p.strip()
            ]

            tasks.extend(parts)

        else:
            tasks.append(
                f"Retrieve information for: {query}"
            )

            tasks.append(
                "Generate answer"
            )

        return tasks