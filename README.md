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

After building the site, validate generated math, local images, and graph integrity:

```sh
python scripts/validate_site.py generated
```
