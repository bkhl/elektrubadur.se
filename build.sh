#!/bin/bash

set -e

shopt -s globstar

# Build
gutenberg build

# Clean HTML
tidy -config tidy.conf public/**/*.html || exit_code=$?
if (( exit_code > 1 )); then
    exit 1
fi

# Clean XML
for xml_file in public/**/*.xml; do
    xmlstarlet fo \
        --noindent \
        --nocdata \
        --nsclean \
        --encode 'utf-8' \
        "$xml_file" | sponge "$xml_file"
done
