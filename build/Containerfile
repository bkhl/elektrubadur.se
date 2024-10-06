FROM  ghcr.io/hugomods/hugo:0.135.0 as hugo

FROM docker.io/library/alpine:latest

COPY --from=hugo /usr/bin/hugo /usr/local/bin/hugo

RUN apk add --no-cache \
    bash \
    git \
    tzdata \
    xmlstarlet \
    tidyhtml
