DOMAIN := 'elektrubadur.se'
IMAGE := 'elektrubadur-builder'

default:
    just --list

build_image:
    podman build -f Containerfile -t '{{ IMAGE }}' .

in_container *args: build_image
    podman run --rm -it \
    -v "${HOME}/.config/hut:/root/.config/hut:z" \
    -v "{{ justfile_directory() }}:{{ justfile_directory() }}:z" \
    -w "{{ justfile_directory() }}" \
    '{{ IMAGE }}' \
    just {{ args }}

serve:
    podman run --rm -it \
    -v "{{ justfile_directory() }}:{{ justfile_directory() }}:z" \
    -w "{{ justfile_directory() }}" \
    -p 1313:1313 \
    '{{ IMAGE }}' \
    hugo serve --bind 0.0.0.0

build:
    rm -rf '{{ justfile_directory() }}/public'
    hugo --baseURL 'https://{{ DOMAIN }}/'

package: build
    tar -C public -czf public.tar.gz .

publish: package
    hut pages publish --domain '{{ DOMAIN }}' --site-config ./site-config.json public.tar.gz
