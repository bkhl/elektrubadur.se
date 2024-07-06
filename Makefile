IMAGE := localhost/elektrubadur-builder:latest

export DOMAIN := elektrubadur.se
export OUTPUT_DIR := public

define run
podman run --rm --interactive \
--volume "$(CURDIR):$(CURDIR):z" \
--workdir "$(CURDIR)"
endef

.PHONY: all image build serve validate package publish package_redirect publish_redirect check_links

all:
	make --print-targets

image:
	podman build -f Containerfile -t $(IMAGE) .

build: image
	$(run) --env DOMAIN --env OUTPUT_DIR $(IMAGE) bash build.sh

serve: image
	$(run) --publish '1313:1313' $(IMAGE) hugo serve --bind 0.0.0.0

validate: build
	$(run) ghcr.io/validator/validator:latest vnu --skip-non-html --also-check-css --also-check-svg public

package: build validate
	tar -C public -czf public.tar.gz .

publish: package
	hut pages publish --domain $(DOMAIN) --site-config ./site-config.json public.tar.gz

package_redirect:
	tar -C redirect -czf redirect.tar.gz .

publish_redirect: package_redirect image
	for domain in www.elektrubadur.se bkhl.elektrubadur.se bkhl.srht.site; do hut pages publish --domain $$domain --site-config ./site-config-redirect.json redirect.tar.gz; done

check_links:
	$(run) docker.io/tennox/linkcheck:latest --show-redirects --check-anchors --skip-file linkcheck_skipfile.txt --external $(DOMAIN)
