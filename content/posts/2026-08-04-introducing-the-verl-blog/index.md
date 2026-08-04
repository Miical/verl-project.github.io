---
title: "Introducing the verl blog"
date: 2026-08-04
authors:
  - "verl-project"
summary: "verl now has its own blog. It exists so that the people who build features can explain them properly."
image: "cover.png"
tags:
  - announcement
  - community
math: false
toc: true
---

verl now has a blog, and it is open to contributors from day one. If you have
landed something in verl and want to explain how it works, you can publish it
here by opening a pull request.

## What gets published here

Writing that helps someone understand verl better. Some of the shapes that
takes:

- **Feature deep dives** — the design behind something that landed, including
  the approaches that were tried and rejected.
- **Performance work** — with hardware, model, and baseline stated, so the
  numbers mean something.
- **Recipes and case studies** — end-to-end accounts of training something real.
- **Release deep dives** — what changed and why it matters.
- **… and anything else you think is worth explaining.** The list above is a
  starting point, not a set of boxes to fit into.

None of this replaces the [documentation](https://verl.readthedocs.io/en/latest/).
The docs describe how the current version works and are kept up to date; a post
captures the reasoning behind a change at the time it was made. If what you are
writing is reference material, it belongs in the docs instead.

## Publishing is a pull request

The whole point of hosting this in the project's own repository is that the
contribution path is the one you already use. A post is a directory:

```text
content/posts/2026-08-04-your-post-slug/
├── index.md
└── cover.png
```

Its front matter declares who wrote it and what it says:

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
---
```

Open a pull request and CI validates the front matter and builds the site. A
maintainer reviews it for accuracy. On merge, the site redeploys on its own.

One thing worth doing first: open an issue with the idea before you start
drafting. A maintainer can tell you early whether the topic fits and whether
somebody else is already writing it, which is a lot cheaper than finding out
once the draft is done.

Full details are on the [Write for us](/contribute/) page.

## Attribution

Posts stay attributed to the people who wrote them. Your name stays on the
byline rather than being replaced by a generic project account, and each author
name becomes an archive page collecting that person's posts.

You also keep the copyright in what you write. Publishing here does not sign
anything away, and nothing stops you from putting the same piece on your own
site as well.

## What happens next

That is up to the community. A blog only works if people write for it, and the
person best placed to explain a piece of verl is usually the one who built it.

So if you have landed something in verl and found yourself explaining it more
than twice — in a Slack thread, in a code review, in an issue comment — that is
a post waiting to be written. Writing it down once, properly, saves the next
person the same conversation, and it is one of the more lasting ways to
contribute to an open source project.

Have a look at [Write for us](/contribute/) and open a pull request. We are
happy to help with drafts, and just as happy to see a rough one.
