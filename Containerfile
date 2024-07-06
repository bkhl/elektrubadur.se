FROM docker.io/library/alpine:latest

RUN apk add --no-cache \
    bash \
    git \
    hugo \
    tzdata \
    xmlstarlet \
    tidyhtml
