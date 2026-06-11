"""Langfuse tracing integration"""

from __future__ import annotations

import time
from typing import List, Dict, Any, Optional

from langfuse import Langfuse


class QueryTracer:
    """Trace queries with Langfuse"""

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        host: str = "https://cloud.langfuse.com",
    ):
        self.langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )

    async def trace_query(
        self,
        query: str,
        steps: list,
    ) -> None:
        """Trace query execution"""

        if not query:
            raise ValueError("query cannot be empty")

        trace = self.langfuse.trace(
            name="rag_query",
            input={"query": query},
            metadata={
                "step_count": len(steps),
            },
        )

        try:
            for idx, step in enumerate(steps):
                start_time = time.time()

                generation = trace.span(
                    name=step.get(
                        "name",
                        f"step_{idx}",
                    ),
                    metadata=step.get(
                        "metadata",
                        {},
                    ),
                    input=step.get("input"),
                )

                generation.end(
                    output=step.get("output"),
                    metadata={
                        "duration_ms": round(
                            (time.time() - start_time)
                            * 1000,
                            2,
                        ),
                        **step.get(
                            "metrics",
                            {},
                        ),
                    },
                )

            trace.update(
                output={
                    "status": "completed",
                }
            )

        except Exception as exc:
            trace.update(
                level="ERROR",
                status_message=str(exc),
            )
            raise

        finally:
            self.langfuse.flush()