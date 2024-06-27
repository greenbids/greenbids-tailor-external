ARG PYTHON_VERSION

FROM docker.io/library/python:${PYTHON_VERSION}-slim

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y autoremove && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home greenbids

USER greenbids

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["greenbids-tailor"]
CMD ["run"]

ARG TAILOR_VERSION
#Waiting to publish python package
#RUN pip3 install --no-cache-dir greenbids-tailor==${TAILOR_VERSION}
