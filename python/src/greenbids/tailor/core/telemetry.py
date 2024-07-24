from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import metrics, trace
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from greenbids.tailor.core._version import __version__

meter_provider = metrics.MeterProvider(
    metric_readers=([PeriodicExportingMetricReader(OTLPMetricExporter())])
)
tracer_provider = trace.TracerProvider()
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

instrumentation_root = "greenbids.tailor"

meter = meter_provider.get_meter(instrumentation_root, __version__)
tracer = tracer_provider.get_tracer(instrumentation_root, __version__)
