"""Prepare copied content for Zensical and render ``[[wikilinks]]`` as links."""

from __future__ import annotations

import re
import shutil
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.build_graph import navigation_pages, page_title  # noqa: E402
from scripts.graph_model import GraphPage, route_for_source, rewrite_wikilinks


def main() -> None:
    project = tomllib.loads((REPO_ROOT / "zensical.toml").read_text(encoding="utf-8"))["project"]
    source_dir = REPO_ROOT / "content"
    output_dir = (REPO_ROOT / project["docs_dir"]).resolve()
    if output_dir == source_dir.resolve() or REPO_ROOT not in output_dir.parents:
        raise ValueError("Zensical docs_dir must be a separate directory inside the project")

    graph_asset = source_dir / "assets" / "js" / "graph.json"
    if not graph_asset.is_file():
        raise FileNotFoundError("Generate the graph first with scripts/build_graph.py")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(source_dir, output_dir, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))

    nav_titles = dict(navigation_pages(project["nav"]))
    source_files = sorted(source_dir.rglob("*.md"))
    pages: list[GraphPage] = []
    content_by_source: dict[str, str] = {}
    for source_path in source_files:
        src_uri = source_path.relative_to(source_dir).as_posix()
        markdown = source_path.read_text(encoding="utf-8")
        content_by_source[src_uri] = markdown
        pages.append(
            GraphPage(
                src_uri=src_uri,
                title=nav_titles.get(src_uri) or page_title(markdown, src_uri),
                url=route_for_source(src_uri),
                markdown=markdown,
                is_index=source_path.name == "index.md",
            )
        )

    converted = 0
    unresolved: list[tuple[str, str]] = []
    for src_uri, markdown in content_by_source.items():
        rendered, missing = rewrite_wikilinks(
            markdown,
            src_uri,
            pages,
            project.get("site_url", ""),
        )
        converted += len(re.findall(r"\[\[[^\]]+\]\]", markdown)) - len(
            re.findall(r"\[\[[^\]]+\]\]", rendered)
        )
        unresolved.extend((src_uri, target) for target in missing)
        (output_dir / src_uri).write_text(rendered, encoding="utf-8")

    if unresolved:
        sample = "\n".join(f"  {source}: [[{target}]]" for source, target in unresolved[:30])
        raise ValueError(f"Could not resolve {len(unresolved)} wikilink(s):\n{sample}")

    print(f"Prepared {len(source_files)} Markdown pages and converted {converted} wikilink(s).")


if __name__ == "__main__":
    main()
