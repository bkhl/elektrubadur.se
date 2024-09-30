#!/bin/bash

set -xeuo pipefail

pushd "${SOURCE}"

git config --global user.name "$(git log -1 --pretty='%an')"
git config --global user.email "$(git log -1 --pretty='%ae')"
message="$(git log -1 --pretty='%B')"

popd

install -v -m 0644 "${SOURCE}/statichost.yml" "${PUBLIC}"
mv "${PREV_PUBLIC}/.git" -t "${PUBLIC}"

pushd "${PUBLIC}"

if git diff-index --quiet HEAD --; then
    # No changes to commit.
    exit 0
fi

git remote set-url origin "https://${GITHUB_ACTOR}:${GITHUB_TOKEN}@github.com/bkhl/elektrubadur.se.git"
git add --all
git commit --message="${message}"
git push origin public:public

popd
