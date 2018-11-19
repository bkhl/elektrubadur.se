#!/bin/bash

set -e

shopt -s globstar

PREFIX="http://elektrubadur.se"

while getopts ":l" opt; do
  case $opt in
    l)
      PREFIX="$(pwd)/public"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit
      ;;
  esac
done

# Build
zola build

# Replace URLs for local display
find public \
    -type f \
    \( \
        -name '*.html' \
        -or -name 'robots.txt' \
        -or -name '*.xml' \
    \) \
    -exec sed -i "s@__PREFIX__@${PREFIX}@g" '{}' ';'

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
