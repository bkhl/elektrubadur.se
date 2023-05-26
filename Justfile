DOMAIN := 'elektrubadur.se'

default:
    just --list

build_image:
    podman build -f Containerfile -t elektrubadur-builder .

in_container *args: build_image
    podman run --rm -it \
    -v "${HOME}/.config/hut:/root/.config/hut:z" \
    -v "{{ justfile_directory() }}:{{ justfile_directory() }}:z" \
    -w "{{ justfile_directory() }}" \
    elektrubadur-builder \
    just {{ args }}

build:
    #!/bin/bash

    set -xeuo pipefail

    output_dir=''{{ justfile_directory() }}/public''

    rm -rf "${output_dir}"

    zola build \
        --base-url='https://{{ DOMAIN }}' \
        --output-dir="${output_dir}"

    find "${output_dir}" -type f -iname '*.html' \
        -exec tidy \
            --quiet yes \
            --show-warnings no \
            --tidy-mark no \
            --vertical-space no \
            --wrap 0 \
            --write-back yes \
            {} '+' \
            || (($?==1 ? 1 : 0))

    find "${output_dir}" -type f -iname '*.xml' | while read f; do
        tempfile="$(mktemp -t xmlstarlet.XXXXXXXX)"
        xmlstarlet fo \
            --noindent \
            --nocdata  \
            --nsclean \
            --encode utf-8 \
            "${f}" > "${tempfile}" && mv -v "${tempfile}" "${f}"
    done

package: build
    tar -C public -czf public.tar.gz .

publish: package
    hut publish -d '{{ DOMAIN }}' public.tar.gz
