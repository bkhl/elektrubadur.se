#!/usr/bin/env bash

set -o errexit
set -o nounset

# Usage: fetch_website.sh URL DIRECTORY
#
# URL - URL, pointing to ZIP file containing single directory named 'public'.
# DIRECTORY - Target directory, to deploy the web site to.

main() {
    local artefact_url=$1
    local destination=$2

    local temp_zip_file
    temp_zip_file=$(mktemp --suffix=.zip)

    local temp_dir
    temp_dir=$(mktemp -d)
    
    local public_dir="$temp_dir/public"

    curl --silent --location "$artefact_url" > "$temp_zip_file"

    unzip -q -d "$temp_dir" "$temp_zip_file"

    rsync --archive --quiet --delete-delay "$public_dir/" "$destination"

    rm "$temp_zip_file"
    rm -r "$temp_dir"
}

main "$@"
