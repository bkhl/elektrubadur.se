#!/bin/bash

set -xeuo pipefail


# Get Git committer and commit message.

pushd "${SOURCE}"

git config --global user.name "$(git log -1 --pretty='%an')"
git config --global user.email "$(git log -1 --pretty='%ae')"
message="$(git log -1 --pretty='%B')"

popd


# Move .git repo into artifact directory.

mv "${PREV_PUBLIC}/.git" -t "${PUBLIC}"


# Commit and push changes

pushd "${PUBLIC}"

if git diff-index --quiet HEAD --; then
    # No changes to commit.
    exit 0
fi

git remote set-url origin "${PUSH_URL}"
git add --all

if git diff --quiet HEAD --; then
    # No changes
    exit 0
fi

git commit --message="${message}"
git push origin public:public

popd


# Trigger publication at Statichost.eu
curl \
    --no-progress-meter \
    --fail \
    --request POST \
    "https://builder.statichost.eu/${SITE_NAME}"
