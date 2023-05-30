FROM docker.io/library/alpine:edge

RUN apk add --no-cache \
    bash \
    git \
    just \
    hugo \
    tzdata \
    xmlstarlet \
    tidyhtml \
    hut
