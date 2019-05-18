#!/usr/bin/env bash

set -o errexit
set -o nounset
 
# Usage: fetch_website.sh URL DIRECTORY
#
# URL - URL, pointing to ZIP file containing single directory named 'public'.
# DIRECTORY - Target directory, to deploy the web site to.

main() {
    local artifact_url=$1
    local destination=$2

    local temp_dir
    temp_dir=$(mktemp -d)

    local etag_file=".artifact_etag"
    local old_etag_file="$destination/$etag_file"
    local temp_zip_file="$temp_dir/artifact.zip"
    local new_etag_file="$temp_dir/public/$etag_file"
    local temp_public_dir="$temp_dir/public"

    mkdir "$temp_public_dir"

    # Get etag of latest build.
    curl --silent --location --head "$artifact_url" \
        | grep '^etag: ' \
        | tail -1 \
        | sed 's/^etag: "\(.*\)"\r$/\1/' \
        > "$new_etag_file"

    # Return after clean-up if etag matches currently installed version.
    if [[ -f "$old_etag_file" ]] && cmp --silent "$old_etag_file" "$new_etag_file"; then
        rm -r "$temp_dir"
        return
    fi

    # Fetch and deploy website.
    curl --silent --location "$artifact_url" > "$temp_zip_file"
    unzip -q -d "$temp_dir" "$temp_zip_file"
    rsync --archive --quiet --delete-delay "$temp_public_dir/" "$destination"

    # Clean up.
    rm -r "$temp_dir"
}

main "$@"
