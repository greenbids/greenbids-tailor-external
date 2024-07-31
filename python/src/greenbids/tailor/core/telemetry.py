import datetime
import logging
import os

from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk import _logs as logs
from opentelemetry.sdk import metrics, trace
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .logging import RateLimitingFilter

meter_provider = metrics.MeterProvider(
    metric_readers=([PeriodicExportingMetricReader(OTLPMetricExporter())])
)

tracer_provider = trace.TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

logger_provider = logs.LoggerProvider()
logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))

handler = logs.LoggingHandler(
    level=logging.getLevelNamesMapping()[
        # Only report error messages by default
        os.environ.get("GREENBIDS_TAILOR_SUPPORT_LOG_LEVEL", "ERROR")
    ],
    logger_provider=logger_provider,
)
# Add a rate limiter to avoid support stack overwhelm
handler.addFilter(
    RateLimitingFilter(
        count=int(os.environ.get("GREENBIDS_TAILOR_SUPPORT_COUNT", 30)),
        per=datetime.timedelta(minutes=1),
    )
)
