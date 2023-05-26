FROM docker.io/library/alpine:edge

RUN apk add --no-cache hut git just hugo tzdata
