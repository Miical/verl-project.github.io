---
# Shown as the page title, the <title> tag and the social card headline.
title: "{{ replace .Name "-" " " | title }}"

# Publication date. A date in the future keeps the post unpublished until then,
# which is handy for coordinating with a release.
date: {{ .Date }}

# One or more names. Use the team or the people who did the work — whatever you
# want readers to see. Each name gets its own archive page.
authors:
  - "your name or team"

# One or two sentences, 240 characters or fewer. This is the card blurb, the
# meta description and the social card text, so make it concrete rather than
# promotional. Avoid line breaks.
summary: ""

# Optional cover image. Put the file next to this index.md and reference it by
# filename; it will be resized and converted to WebP automatically.
# image: "cover.png"

# Pick from the existing tags where you can, so the archive pages stay useful.
# Common ones: release, performance, recipes, rollout, training, megatron,
# fsdp, sglang, vllm, multi-turn, agent, case-study.
tags:
  - ""

# Set to true if the post contains LaTeX. Loads KaTeX only when needed.
math: false

# Set to false to hide the table of contents on a short post.
toc: true

draft: true
---

Open with the result, not the background. A reader who stops after the first
paragraph should still know what changed and whether it affects them.

## Why this was needed

## How it works

## Results

## What's next
