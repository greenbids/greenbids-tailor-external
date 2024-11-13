#! /usr/bin/env sh

set -eux

cd python || exit
version=$(hatch version)
hatch build -t wheel
python3 -m http.server -d dist &
server_job="$!"
cd ..

docker_version=$(echo "$version" | tr '+' '-')
docker build \
    --build-arg PYTHON_VERSION=3.12 \
    --build-arg TAILOR_VERSION_SPEC="==$version" \
    --build-arg 'PIP_EXTRA_ARGS=--pre --index-url=http://localhost:8000/ --extra-index-url=https://pypi.org/simple' \
    --network host \
    -t "ghcr.io/greenbids/tailor:${docker_version}" \
    container
kill $server_job
