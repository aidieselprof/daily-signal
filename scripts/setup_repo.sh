#!/usr/bin/env bash
set -e
RN="${1:-daily-signal}"
git init
git add .
git commit -m "Initial commit — Money Autopilot v2"
gh repo create "$RN" --public --source . --remote origin --push
