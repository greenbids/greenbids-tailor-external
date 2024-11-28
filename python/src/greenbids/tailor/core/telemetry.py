import datetime
import logging
import uuid
import os

from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk import _logs as logs
from opentelemetry.sdk import metrics, trace, resources
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics.export import (
    MetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
import prometheus_client


from .logging_ import RateLimitingFilter
from greenbids.tailor.core import version

_logger = logging.getLogger(__name__)

RESOURCE = resources.Resource.create(
    {
        resources.SERVICE_NAMESPACE: str(
            os.environ.get("GREENBIDS_TAILOR_API_USER", "Unknown")
        ),
        resources.SERVICE_INSTANCE_ID: uuid.uuid1().hex,
        resources.SERVICE_VERSION: version,
    }
)

_OTLP_METRICS_READER = PeriodicExportingMetricReader(OTLPMetricExporter())
metric_readers: list[MetricReader] = [_OTLP_METRICS_READER]
if str(os.environ.get("OTEL_EXPORTER_PROMETHEUS_ENABLED")).lower() == "true":
    requested_port = os.environ.get("OTEL_EXPORTER_PROMETHEUS_PORT")
    port = int(requested_port or 9464)
    while True:
        try:
            prometheus_client.start_http_server(port=port)
            if str(port) != requested_port:
                _logger.warning("Prometheus server as been started on port %d", port)
            break
        except OSError:
            port += 1
    metric_readers.append(PrometheusMetricReader())
meter_provider = metrics.MeterProvider(metric_readers=metric_readers, resource=RESOURCE)

_OTLP_TRACES_PROCESSOR = BatchSpanProcessor(OTLPSpanExporter())
tracer_provider = trace.TracerProvider(resource=RESOURCE)
tracer_provider.add_span_processor(_OTLP_TRACES_PROCESSOR)

_OTLP_LOGS_PROCESSOR = BatchLogRecordProcessor(OTLPLogExporter())
logger_provider = logs.LoggerProvider(resource=RESOURCE)
logger_provider.add_log_record_processor(_OTLP_LOGS_PROCESSOR)

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
