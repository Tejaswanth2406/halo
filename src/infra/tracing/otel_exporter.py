"""OpenTelemetry exporter"""

from __future__ import annotations

from typing import Dict, Any, Optional
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode


class OTelExporter:
    """Export traces to OpenTelemetry"""

    def __init__(
        self,
        tracer_name: str = "rag-platform",
        service_version: str = "1.0.0",
    ):
        self.tracer = trace.get_tracer(
            tracer_name,
            service_version,
        )

    async def export_trace(
        self,
        trace_data: Dict[str, Any],
    ) -> None:
        """Export trace"""

        if not trace_data:
            raise ValueError("trace_data cannot be empty")

        span_name = trace_data.get(
            "name",
            "unknown-operation",
        )

        with self.tracer.start_as_current_span(
            span_name,
            kind=SpanKind.INTERNAL,
        ) as span:

            for key, value in trace_data.get(
                "attributes",
                {},
            ).items():
                span.set_attribute(
                    str(key),
                    str(value),
                )

            for event in trace_data.get(
                "events",
                [],
            ):
                span.add_event(
                    name=event.get("name", "event"),
                    attributes=event.get(
                        "attributes",
                        {},
                    ),
                )

            error = trace_data.get("error")

            if error:
                span.record_exception(
                    Exception(str(error))
                )
                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(error),
                    )
                )
            else:
                span.set_status(
                    Status(StatusCode.OK)
                )

            trace_id = trace_data.get("trace_id")
            if trace_id:
                span.set_attribute(
                    "trace.id",
                    trace_id,
                )

            span.set_attribute(
                "exported",
                True,
            )