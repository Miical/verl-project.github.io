# Writing for the verl blog

If you have landed something in verl and want to explain how it works, this is
the place to write it up.

A friendlier version of this guide, with rendered examples, lives at
<https://verl-project.github.io/contribute/>. This file is the reference.

## Before you start

Open an issue with your idea before you start drafting, using the **Blog post
proposal** template. A maintainer can tell you early whether the topic fits and
whether somebody else is already writing it, which is a lot cheaper than finding
out once the draft is done.

## What we publish

Writing that helps someone understand verl better:

- Feature deep dives — the design behind something that landed, including the
  approaches that were tried and rejected.
- Performance work — with hardware, model and baseline stated.
- Recipes and case studies — end-to-end accounts of training something real.
- Release deep dives — what changed and why, beyond the changelog.
- … and anything else worth explaining. The list is a starting point, not a set
  of categories. Open an issue if you want to check whether an idea fits.

A post is not a substitute for the [documentation](https://verl.readthedocs.io/en/latest/).
Docs describe how the current version behaves and are kept current; a post
captures the reasoning behind a change at the time it was made. Reference
material belongs in the docs.

## Layout

One directory per post, so images travel with the text:

```text
content/posts/2026-08-04-async-rollout/
├── index.md
├── cover.png
└── throughput.png
```

The directory name must be `YYYY-MM-DD-lowercase-slug`. Scaffold it with:

```bash
hugo new content posts/2026-08-04-async-rollout/index.md
```

## Front matter reference

```yaml
---
title: "Async rollout in verl"
date: 2026-08-04
authors:
  - "Jane Doe"
  - "John Smith"
summary: "Async rollout overlaps generation with training and cuts idle GPU time on long-horizon tasks."
image: "cover.png"
tags:
  - rollout
  - performance
math: false
toc: true
---
```

| Key | Required | Notes |
| --- | --- | --- |
| `title` | yes | Under 90 characters reads better in cards. |
| `date` | yes | Unquoted `YYYY-MM-DD`. Must match the directory prefix. A future date holds the post back until then. |
| `authors` | yes | A list. Real names, GitHub handles or a team name. Each value gets an archive page. |
| `summary` | yes | 240 characters or fewer, single line. Used as the card blurb, meta description and social card text. |
| `image` | no | Filename relative to the post directory. Resized and converted to WebP at build time — commit the original. Around 1200×630 works well. |
| `tags` | no | Lowercase. Reuse existing tags where you can. |
| `math` | no | `true` loads KaTeX. Leave it off if the post has no equations. |
| `toc` | no | `false` hides the table of contents on short posts. |
| `draft` | no | `true` keeps it out of production builds. Remove it when you are ready. |

`scripts/check_posts.py` enforces the required keys, the summary length, the
directory naming and the image paths. CI runs it on every pull request, so run
it yourself first:

```bash
python3 scripts/check_posts.py
```

## Writing

Fenced code blocks are syntax highlighted. Line numbers are off by default,
because they get in the way of copying shell commands; turn them on per block
when you want to refer to a specific line:

````markdown
```python {linenos=true}
def compute_advantage(...):
    ...
```
````

Plain markdown images become captioned figures automatically — the alt text is
the caption. Two shortcodes cover the rest:

```markdown
{{< figure src="throughput.png" alt="Throughput by batch size" caption="Decode throughput, 8×H100, Qwen3-8B." width="80%" >}}

{{< note type="warning" title="Version note" >}}
This API changed in v0.8. On earlier versions, use `foo` instead.
{{< /note >}}
```

`note` accepts `type="info"` (default), `tip`, `warning` or `caution`.

With `math: true` in the front matter, write `$$...$$` for display equations and
`\(...\)` inline.

### House style

- **Lead with the outcome.** State the result in the first paragraph. A reader
  who stops there should still know what changed and whether it affects them.
- **Numbers need context.** Hardware, model, sequence length, batch size,
  baseline. A speedup without a baseline is not a result.
- **Link to the code.** Pull requests, issues and file paths let readers verify
  what you describe.
- **Assume RL knowledge, not subsystem knowledge.** Expand an acronym the first
  time you use it.
- **English is the default.**

## Checklist before opening the pull request

- [ ] `python3 scripts/check_posts.py` passes
- [ ] `hugo --buildDrafts --buildFuture` builds without errors
- [ ] `python3 scripts/check_links.py` reports no broken internal links
- [ ] `draft: true` removed
- [ ] Images live in the post directory and are referenced by filename
- [ ] Numbers, if any, state the hardware and the baseline

## Review

A maintainer reviews for accuracy and clarity. Once it is merged, the site
redeploys automatically and your post is live within a couple of minutes.

## Copyright

You keep the copyright in your post. Opening a pull request grants verl-project
the right to publish it here under your byline, and that is all it grants: you
stay free to put the same piece on your own site or anywhere else. The post
remains attributed to you indefinitely.
