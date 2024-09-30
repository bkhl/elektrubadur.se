#!/bin/bash

set -xeuo pipefail

: "${DOMAIN:=elektrubadur.se}"
: "${DESTINATION:=public}"

rm -rf "${DESTINATION}"

hugo --baseURL="https://${DOMAIN}" --destination="${DESTINATION}"

find "${DESTINATION}" -type f -iname '*.html' \
    -exec tidy \
        --quiet yes \
        --show-warnings no \
        --tidy-mark no \
        --vertical-space no \
        --wrap 0 \
        --write-back yes \
        --indent auto \
        {} '+' \
        || (($?==1 ? 1 : 0))

find "${DESTINATION}" -type f -iname '*.xml' | while read f; do
    tempfile="$(mktemp -t "$(basename "${f}")".XXXXXXXX)"
    xmlstarlet fo \
        --nocdata  \
        --nsclean \
        --encode utf-8 \
        "${f}" > "${tempfile}" && mv -v "${tempfile}" "${f}"
done
