# verl blog

Source for the [verl](https://github.com/verl-project/verl) blog, published at
**https://verl-project.github.io/**.

The site is a [Hugo](https://gohugo.io/) static site with a theme written for
this repository. It is built and deployed by GitHub Actions on every push to
`main`; there is nothing to publish by hand.

**Want to write a post?** Read [CONTRIBUTING.md](CONTRIBUTING.md), or the same
guide with examples on [the site itself](https://verl-project.github.io/contribute/).

## Running it locally

[Hugo](https://gohugo.io/installation/) v0.153.0 or newer is the only
requirement — a single binary with no runtime dependencies. The standard
edition is enough.

```bash
git clone https://github.com/verl-project/verl-project.github.io.git
cd verl-project.github.io
hugo server --buildDrafts --buildFuture
```

The site is at http://localhost:1313 and reloads as you edit. Drop
`--buildDrafts` to see exactly what production will show.

## Adding a post

```bash
hugo new content posts/2026-08-04-my-post-slug/index.md
```

That scaffolds `content/posts/<date>-<slug>/index.md` with a commented front
matter template. Write the post, drop images in the same directory, remove
`draft: true`, and open a pull request. See [CONTRIBUTING.md](CONTRIBUTING.md)
for the field reference and house style.

## Repository layout

```text
archetypes/post.md        Front matter template used by `hugo new`
assets/css/               Stylesheet and generated syntax highlighting
content/posts/            One directory per post, images included
content/contribute.md     The public submission guide
layouts/                  Templates. No external theme is used.
  _partials/              Header, footer, cards, metadata, icons
  _shortcodes/            {{< figure >}} and {{< note >}}
  _markup/                Render hooks for markdown images and links
scripts/                  Validation and asset generation, all Python
static/                   Files copied verbatim, currently just the favicon
```

## Checks

Both run in CI on every pull request, and both are worth running locally before
you push:

```bash
python3 scripts/check_posts.py     # front matter: required keys, summary length, image paths
hugo --buildDrafts --buildFuture   # the build itself
python3 scripts/check_links.py     # internal links in public/ that resolve to nothing
```

`check_posts.py` needs PyYAML (`pip install pyyaml`); `check_links.py` uses only
the standard library.

## Regenerating assets

Neither of these needs to be run for a normal post. They exist so the generated
files in the repository can be reproduced rather than being mystery binaries:

```bash
python3 scripts/gen_syntax_css.py     # assets/css/syntax.css
python3 scripts/gen_images.py         # the drawn post cover images
```

`gen_images.py` needs Pillow and matplotlib (for its bundled DejaVu fonts).

## Deployment

`.github/workflows/deploy.yml` builds with `--minify` and publishes to GitHub
Pages on pushes to `main`. It also runs on a daily schedule so that a
future-dated post goes live on its date without anyone touching the repository.

`.github/workflows/ci.yml` runs on pull requests: front matter validation, a
full build including drafts and future-dated posts, and the internal link check.
