ARG PYTHON_VERSION

FROM docker.io/library/python:${PYTHON_VERSION}-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG TAILOR_VERSION

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y autoremove && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home greenbids

USER greenbids

RUN python3 -m venv /home/greenbids/venv
ENV VIRTUAL_ENV=/home/greenbids/venv
ENV PATH="/home/greenbids/venv/bin:$PATH"

RUN pip3 install --no-cache-dir wheel
#Waiting to publish python package
#RUN pip3 install --no-cache-dir greenbids-tailor[all]==${TAILOR_VERSION}

ENV PORT=8080
EXPOSE 8080

ENTRYPOINT ["greenbids-tailor"]
