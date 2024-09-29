IMAGE := localhost/elektrubadur-builder:latest

export DOMAIN := elektrubadur.se
export DESTINATION := public

define run
podman run --rm --interactive \
--volume "$(CURDIR):$(CURDIR):z" \
--workdir "$(CURDIR)"
endef

.PHONY: all image build serve validate check_links

all:
	make --print-targets

image:
	podman build -f Containerfile -t $(IMAGE) .

build: image
	$(run) --env DOMAIN --env DESTINATION $(IMAGE) bash build.sh

serve: image
	$(run) --publish '1313:1313' $(IMAGE) hugo serve --bind 0.0.0.0

validate: build
	$(run) ghcr.io/validator/validator:latest vnu --skip-non-html --also-check-css --also-check-svg public

check_links:
	$(run) docker.io/tennox/linkcheck:latest --show-redirects --check-anchors --skip-file linkcheck_skipfile.txt --external $(DOMAIN)
