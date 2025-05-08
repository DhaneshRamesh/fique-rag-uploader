#!/bin/bash

git config --global user.name "github-actions[bot]"
git config --global user.email "github-actions[bot]@users.noreply.github.com"

git add fique_articles.jsonl
git commit -m "🤖 Auto-update fique_articles.jsonl from scraper" || exit 0  # Skip if no changes
git push https://x-access-token:${GH_PAT}@github.com/${GITHUB_REPOSITORY}.git HEAD:main
