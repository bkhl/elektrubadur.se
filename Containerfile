FROM docker.io/library/alpine:edge

RUN apk add --no-cache bash hut just zola tidyhtml xmlstarlet
