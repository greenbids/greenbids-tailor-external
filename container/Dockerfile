ARG PYTHON_VERSION=3

FROM docker.io/library/python:${PYTHON_VERSION}-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y autoremove && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home greenbids

EXPOSE 8000

ENV WEB_CONCURRENCY=4
ENV OTEL_SERVICE_NAME="greenbids-tailor"
ENV OTEL_TRACES_SAMPLER=parentbased_traceidratio
ENV OTEL_TRACES_SAMPLER_ARG=0.0001
ENV OTEL_EXPORTER_OTLP_ENDPOINT="https://tailor.greenbids.ai/"
ENV OTEL_EXPORTER_OTLP_HEADERS="Greenbids-Tailor=true"

ENTRYPOINT ["greenbids-tailor"]
CMD ["run"]

ARG PIP_INDEX_URL="https://pypi.org/simple"
ARG PIP_EXTRA_ARGS=""
ARG TAILOR_VERSION_SPEC
RUN pip3 --version && pip3 install --no-cache-dir ${PIP_EXTRA_ARGS} greenbids-tailor${TAILOR_VERSION_SPEC}

USER greenbids
