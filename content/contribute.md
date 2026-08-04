---
title: "Write for the verl blog"
summary: "How to propose, write and ship a post about work you have done in verl."
---

If you have landed something in verl and want to explain how it works, 
this blog is the place to write it up. 

{{< note type="tip" title="Talk to us before you write" >}}
Open an issue with your idea before you start drafting. 
A maintainer can tell you early whether the topic fits and whether
somebody else is already writing it, which is a lot cheaper than finding out
once the draft is done.
{{< /note >}}

## What we publish

Posts that help someone else understand verl better. In practice that tends to
be one of:

- **Feature deep dives.** You landed something non-trivial and want to explain
  the design, the trade-offs you rejected, and how to use it.
- **Performance work.** A change with numbers attached. Say what hardware, what
  model, what batch shape, and what you measured against.
- **Recipes and case studies.** An end-to-end account of training something
  real, including the parts that did not work at first.
- **Release notes with substance.** What actually changed and why it matters.
- **… and anything else worth explaining.** Treat the list as a starting point
  rather than a set of boxes to fit into. If you are unsure whether an idea
  fits, open an issue and ask.

One thing this blog is not is a substitute for the
[documentation](https://verl.readthedocs.io/en/latest/). Docs describe how the
current version behaves and get updated as it changes; a post captures the
reasoning behind a change at the time it was made. Reference material belongs in
the docs — and both are good places to contribute.

## The short version

1. Open an issue on the [blog repository](https://github.com/verl-project/verl-project.github.io/issues).
2. Fork the repository and create a directory under `content/posts/`, named
   `YYYY-MM-DD-short-slug`.
3. Write `index.md` inside it. Put images in the same directory.
4. Open a pull request. CI checks the front matter and builds the site.
5. A maintainer reviews for accuracy and clarity. Once it is merged, the site
   redeploys automatically and your post is live within a couple of minutes.

## Writing the post

Every post is a directory, not a loose file, so that its images travel with it:

```text
content/posts/2026-08-04-your-post-slug/
├── index.md
├── cover.png
└── throughput-comparison.png
```

The front matter at the top of `index.md` looks like this:

```yaml
---
title: "Async rollout in verl"
date: 2026-08-04
authors:
  - "Jane Doe"
summary: "Async rollout overlaps generation with training and cuts idle GPU time on long-horizon tasks."
image: "cover.png"
tags:
  - performance
math: false
toc: true
---
```

`title`, `date`, `authors` and `summary` are required; CI will reject the pull
request without them. A few notes on the ones that trip people up:

- **`summary`** must be 240 characters or fewer and cannot contain line breaks.
  It is the card blurb, the meta description and the social card text all at
  once. Write what the post concludes, not what it is "about".
- **`authors`** is a list. Use real names, GitHub handles, or a team name —
  whatever you want readers to see. Each value gets an archive page.
- **`image`** is a filename relative to the post directory. Hugo resizes it and
  converts it to WebP at build time, so commit the original rather than a
  hand-shrunk copy. Aim for something around 1200×630 for the cover.
- **`date`** in the future keeps the post unpublished until that date. This is
  the mechanism to use when a post has to land with a release.

If you would rather not write the front matter by hand, scaffold it:

```bash
hugo new content posts/2026-08-04-your-post-slug/index.md
```

### Things the theme gives you

Fenced code blocks are syntax highlighted. Line numbers are off by default,
since they get in the way of copying shell commands — add `{linenos=true}` after
the language when you want to refer to a specific line. Plain markdown images
are turned into captioned figures automatically, with the alt text becoming the
caption. For anything more specific there are two shortcodes:

```markdown
{{</* figure src="throughput.png" alt="Throughput by batch size" caption="Decode throughput, 8×H100, Qwen3-8B." width="80%" */>}}

{{</* note type="warning" title="Version note" */>}}
This API changed in v0.8. On earlier versions, use `foo` instead.
{{</* /note */>}}
```

Set `math: true` in the front matter to load KaTeX, then write `$$...$$` for
display equations and `\(...\)` inline.

### House style

We are not precious about this, but a few things make review faster:

- **Lead with the outcome.** State the result in the first paragraph. Save the
  background for later — readers who need it will keep reading.
- **Numbers need context.** Hardware, model, sequence length, batch size,
  baseline. A speedup with no baseline is not a result.
- **Link to the code.** Pull requests, issues and file paths let readers verify
  what you are describing and go deeper.
- **Write for someone who knows RL but not your subsystem.** Expand an acronym
  the first time you use it.
- **English is the default.** 

## Previewing your work

You need [Hugo](https://gohugo.io/installation/) v0.153.0 or newer. It is a
single binary with no runtime dependencies:

```bash
git clone https://github.com/verl-project/verl-project.github.io.git
cd verl-project.github.io
hugo server --buildDrafts
```

The site is then at `http://localhost:1313` and reloads as you save. Drafts and
future-dated posts only appear with `--buildDrafts` and `--buildFuture`.

## Copyright

You keep the copyright in your post. Opening a pull request grants verl-project
the right to publish it here under your byline, and that is all it grants: you
stay free to put the same piece on your own site or anywhere else. The post
remains attributed to you indefinitely.
