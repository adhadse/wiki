# Wiki
This repo is the origin repo used to build my [wiki](https://wiki.adhadse.com).

## Local Zensical preview

Prepare the graph and render Obsidian-style `[[wikilinks]]` into regular page
links before building or serving with Zensical:

```sh
uv run python scripts/build_graph.py
uv run python scripts/prepare_zensical_content.py
uv run zensical serve --config-file zensical.toml
```

The generated graph JSON is ignored by Git. Prepared content is written to the
ignored `zensical-content/` directory, leaving source notes unchanged.

For a static build, run the same preparation steps before:

```sh
uv run zensical build --config-file zensical.toml --clean
```

The graph combines internal Markdown links, Obsidian wikilinks, and folder
hierarchy. Unresolved wikilinks stop content preparation with an error.

## Obsidian-style links and graph edges

Write a wikilink in a note to create a clickable link and a page-to-page edge
in the graph:

```md
[[ml-data-lifecycle]]
[[ml-data-lifecycle|ML Data Lifecycle]]
[[ml-data-lifecycle#data-collection|Data collection]]
```

The part before `|` identifies the target; the optional text after `|` is the
label shown on the page. You can add a heading after `#` to link to that
section. Targets can be paths relative to the current note, site-relative
paths, or a unique page filename/title. For example, from
`content/ml/mle-for-production/index.md`, `[[ml-data-lifecycle]]` resolves to
the ML Data Lifecycle page. If a filename or title matches more than one page,
use a path to identify the intended note.

The graph builder reads wikilinks from Markdown source, so the edge appears
after the normal graph/content preparation steps above (and in the GitHub Pages
build). Links inside code blocks are left as code, not converted into graph
edges. If a target cannot be resolved, content preparation reports it as an
error; check the target path or title and try again.

After building the site, validate generated math, local images, and graph integrity:

```sh
python scripts/validate_site.py generated
```
