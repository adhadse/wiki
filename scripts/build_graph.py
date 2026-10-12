"""Generate the Obsidian-style graph asset before a Zensical build."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.graph_model import GraphPage, build_graph, write_graph  # noqa: E402


def page_title(markdown: str, src_uri: str) -> str:
    """Return the front-matter title or first Markdown heading, if present."""
    front_matter = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", markdown, re.S)
    if front_matter:
        title = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", front_matter.group(1), re.M)
        if title:
            return title.group(1).strip().strip("\"'")

    heading = re.search(r"^#\s+(.+?)\s*#*\s*$", markdown, re.M)
    if heading:
        return heading.group(1).strip()

    return Path(src_uri).stem.replace("-", " ").replace("_", " ").capitalize()


def navigation_pages(nav: object) -> list[tuple[str, str | None]]:
    """Collect explicitly listed Markdown sources from the Zensical nav."""
    pages: list[tuple[str, str | None]] = []

    def visit(item: object) -> None:
        if isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, dict):
            for label, child in item.items():
                if isinstance(child, str) and child.endswith(".md"):
                    pages.append((child, str(label)))
                else:
                    visit(child)
        elif isinstance(item, str) and item.endswith(".md"):
            pages.append((item, None))

    visit(nav)
    if not pages:
        raise ValueError("No Markdown page paths were found in the nav block")
    return pages


def main() -> None:
    config_file = REPO_ROOT / "zensical.toml"
    content_dir = REPO_ROOT / "content"
    config = tomllib.loads(config_file.read_text(encoding="utf-8"))["project"]
    pages = []

    site_name = config["site_name"]
    site_url = config.get("site_url", "")

    for src_uri, title_override in navigation_pages(config["nav"]):
        source_path = content_dir / src_uri
        if not source_path.is_file():
            raise FileNotFoundError(f"Navigation page does not exist: {source_path}")
        markdown = source_path.read_text(encoding="utf-8")
        route = Path(src_uri).with_suffix("")
        if route.name == "index":
            route = route.parent
        route_text = route.as_posix().strip(".")
        url = "/" + (route_text.strip("/") + "/" if route_text.strip("/") else "")
        pages.append(
            GraphPage(
                src_uri=src_uri,
                title=title_override or page_title(markdown, src_uri),
                url=url,
                markdown=markdown,
                is_index=Path(src_uri).name == "index.md",
            )
        )

    graph, stats = build_graph(pages, site_name, site_url)
    output = write_graph(graph, content_dir)
    edge_counts = stats["edges"]
    print(
        f"Generated {stats['pages']} page nodes, {stats['directories']} directory nodes, "
        f"and {edge_counts['markdown']} Markdown-link / {edge_counts['wikilink']} wiki-link edges "
        f"at {output.relative_to(REPO_ROOT)}."
    )
    if stats["unresolved_internal_links"]:
        print(f"Skipped unresolved local links: {len(stats['unresolved_internal_links'])}")


if __name__ == "__main__":
    main()
