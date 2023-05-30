DOMAIN := 'elektrubadur.se'
IMAGE := 'elektrubadur-builder'

default:
    just --list

build_image:
    podman build -f Containerfile -t '{{ IMAGE }}' .

_in_container *args: build_image
    podman run --rm -it \
    -v "${HOME}/.config/hut:/root/.config/hut:z" \
    -v "{{ justfile_directory() }}:{{ justfile_directory() }}:z" \
    -w "{{ justfile_directory() }}" \
    '{{ IMAGE }}' \
    just {{ args }}

_serve:
    podman run --rm -it \
    -v "{{ justfile_directory() }}:{{ justfile_directory() }}:z" \
    -w "{{ justfile_directory() }}" \
    -p 1313:1313 \
    '{{ IMAGE }}' \
    hugo serve --bind 0.0.0.0

serve:
    @just _in_container _serve

_build:
    #!/bin/bash

    set -xeuo pipefail

    output_dir=''{{ justfile_directory() }}/public''

    rm -rf "${output_dir}"

    hugo --baseURL='https://{{ DOMAIN }}'

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
        tempfile="$(mktemp -t "$(basename "${f}")".XXXXXXXX)"
        xmlstarlet fo \
            --noindent \
            --nocdata  \
            --nsclean \
            --encode utf-8 \
            "${f}" > "${tempfile}" && mv -v "${tempfile}" "${f}"
    done

build:
    @just _in_container _build

validate: build
    podman run --rm -it \
    -v "{{ justfile_directory() }}:{{ justfile_directory() }}:z" \
    -w "{{ justfile_directory() }}" \
    ghcr.io/validator/validator:latest \
    vnu --skip-non-html public

package: build validate
    tar -C public -czf public.tar.gz .

_publish:
    hut pages publish --domain '{{ DOMAIN }}' --site-config ./site-config.json public.tar.gz

publish: package
    just _in_container _publish

package_redirect:
    tar -C redirect -czf redirect.tar.gz .

publish_redirect domain: package_redirect
    hut pages publish --domain '{{ domain }}' --site-config ./site-config-redirect.json redirect.tar.gz
