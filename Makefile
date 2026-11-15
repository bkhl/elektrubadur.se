MAKEFLAGS += --always-make

RUNNER := podman

IMAGE := localhost/elektrubadur-builder:latest

export DOMAIN := elektrubadur.se
export DESTINATION := public

define run
$(RUNNER) run --rm --interactive $(if $(MAKE_TERMOUT),--tty,) \
--volume "$(CURDIR):$(CURDIR):z" \
--workdir "$(CURDIR)"
endef

help:
	make --print-targets

image:
	$(RUNNER) build --file build/Containerfile --tag $(IMAGE) $(shell mktemp -d)

build:
	$(run) --env DOMAIN --env DESTINATION $(IMAGE) bash build/build.sh

serve:
	$(run) --publish '1313:1313' $(IMAGE) hugo serve --bind 0.0.0.0

validate:
	$(run) ghcr.io/validator/validator:latest vnu --skip-non-html --also-check-css --also-check-svg public

clean:
	rm -rf public resources
