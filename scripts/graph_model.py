"""Graph model used by the Zensical site build."""

from __future__ import annotations

import html
import json
import posixpath
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit


@dataclass
class GraphPage:
    """A published Markdown page and the source fields needed for graphing."""

    src_uri: str
    title: str
    url: str
    markdown: str
    is_index: bool = False


FENCED_CODE_RE = re.compile(r"(?ms)^\s*(?:```|~~~)[^\n]*\n.*?^\s*(?:```|~~~)\s*$")
INLINE_CODE_RE = re.compile(r"(`+)[^`\n]*?\1")
INLINE_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(\s*(<[^>]+>|[^)]+)\)")
REFERENCE_DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(\S+)", re.M)
REFERENCE_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\[([^\]]+)\]")
HTML_LINK_RE = re.compile(r"<a\b[^>]*\bhref=[\"']([^\"']+)[\"']", re.I)
WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
WIKI_LINK_TOKEN_RE = re.compile(r"(?P<code>`+[^`\n]*`+)|(?P<wiki>\[\[[^\]]+\]\])")
DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]", re.S)
INLINE_MATH_RE = re.compile(r"(?<!\\)(?<!\$)\$(?!\$).*?(?<!\\)(?<!\$)\$(?!\$)", re.S)


def normalize_source(src_uri: str) -> str:
    path = unquote(src_uri).replace("\\", "/").lstrip("/")
    normalized = posixpath.normpath(path)
    return "" if normalized == "." else normalized


def route_for_source(src_uri: str) -> str:
    route = posixpath.splitext(normalize_source(src_uri))[0]
    if route == "index":
        return "/"
    if route.endswith("/index"):
        route = route[: -len("/index")]
    return "/" + route.strip("/") + "/" if route.strip("/") else "/"


def route_key(path: str) -> str:
    value = "/" + path.strip("/")
    return value if value != "/" else "/"


def parse_wikilink(payload: str) -> tuple[str, str | None, str | None]:
    target, has_alias, alias = payload.partition("|")
    target_path, has_fragment, fragment = target.partition("#")
    if not has_fragment and has_alias and "#" in alias:
        alias, _, fragment = alias.partition("#")
        has_fragment = True
    return (
        target_path.strip(),
        alias.strip() if has_alias else None,
        fragment.strip() if has_fragment else None,
    )


def _page_resolver(pages: list[GraphPage], site_url: str = ""):
    by_source: dict[str, GraphPage] = {}
    by_route: dict[str, GraphPage] = {}
    by_stem: dict[str, list[GraphPage]] = {}
    by_title: dict[str, list[GraphPage]] = {}
    for page in pages:
        source = normalize_source(page.src_uri)
        by_source[source] = page
        by_source[posixpath.splitext(source)[0]] = page
        by_route[route_key(route_for_source(source))] = page
        by_stem.setdefault(PurePosixPath(source).stem.casefold(), []).append(page)
        by_title.setdefault(page.title.strip().casefold(), []).append(page)

    site_parts = urlsplit(site_url)
    site_host = site_parts.netloc.casefold()
    site_prefix = site_parts.path.rstrip("/")

    def resolve(source_uri: str, target: str) -> GraphPage | None:
        parsed = urlsplit(target.strip())
        if not parsed.path or parsed.path.startswith("assets/"):
            return None
        if parsed.netloc and parsed.netloc.casefold() != site_host:
            return None
        if parsed.scheme and parsed.netloc.casefold() != site_host:
            return None

        target_path = unquote(parsed.path).replace("\\", "/")
        if site_prefix and target_path.startswith(site_prefix + "/"):
            target_path = target_path[len(site_prefix) :]
        if target_path.startswith("/"):
            candidate = posixpath.normpath(target_path.lstrip("/"))
        else:
            candidate = posixpath.normpath(
                posixpath.join(posixpath.dirname(normalize_source(source_uri)), target_path)
            )
        if candidate in {".", ".."} or candidate.startswith("../"):
            return None
        candidate = candidate.lstrip("/")

        if candidate in by_source:
            return by_source[candidate]
        if candidate.endswith(".md"):
            return by_route.get(route_key(route_for_source(candidate)))
        if route_key(candidate) in by_route:
            return by_route[route_key(candidate)]
        for possible in (candidate + ".md", candidate.rstrip("/") + "/index.md"):
            if possible in by_source:
                return by_source[possible]

        stem_candidates = by_stem.get(PurePosixPath(candidate.rstrip("/")).stem.casefold(), [])
        if len(stem_candidates) == 1:
            return stem_candidates[0]
        title_candidates = by_title.get(candidate.strip().casefold(), [])
        return title_candidates[0] if len(title_candidates) == 1 else None

    return resolve


def rewrite_wikilinks(
    markdown: str,
    source_uri: str,
    pages: list[GraphPage],
    site_url: str = "",
) -> tuple[str, list[str]]:
    """Turn Obsidian wikilinks into regular links, leaving code untouched."""
    resolve = _page_resolver(pages, site_url)
    unresolved: list[str] = []
    output: list[str] = []
    in_fence = False
    fence_character = ""
    fence_length = 0

    def replace(match: re.Match) -> str:
        if match.group("code"):
            return match.group(0)
        target, alias, fragment = parse_wikilink(match.group("wiki")[2:-2])
        page = resolve(source_uri, target)
        if page is None:
            unresolved.append(target)
            return match.group(0)
        href = page.url or route_for_source(page.src_uri)
        if fragment:
            slug = re.sub(r"[^\w\- ]", "", unquote(fragment).casefold()).strip()
            href += "#" + re.sub(r"\s+", "-", slug)
        return f"[{alias or page.title}]({href})"

    for line in markdown.splitlines(keepends=True):
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            if not in_fence:
                in_fence = True
                fence_character = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_character and len(marker) >= fence_length:
                in_fence = False
            output.append(line)
        elif in_fence:
            output.append(line)
        elif line.startswith(("    ", "\t")):
            output.append(line)
        else:
            output.append(WIKI_LINK_TOKEN_RE.sub(replace, line))

    return "".join(output), unresolved


def resolve_page_target(
    pages: list[GraphPage], source_uri: str, target: str, site_url: str = ""
) -> GraphPage | None:
    """Resolve a relative, root-absolute, route, basename, or title target."""
    by_source: dict[str, GraphPage] = {}
    by_route: dict[str, GraphPage] = {}
    by_stem: dict[str, list[GraphPage]] = {}
    by_title: dict[str, list[GraphPage]] = {}
    for page in pages:
        source = normalize_source(page.src_uri)
        by_source[source] = page
        by_source[posixpath.splitext(source)[0]] = page
        by_route[route_key(route_for_source(source))] = page
        by_stem.setdefault(PurePosixPath(source).stem.casefold(), []).append(page)
        by_title.setdefault(page.title.strip().casefold(), []).append(page)

    target = target.strip()
    if not target or target.startswith(("#", "data:")):
        return None
    site_parts = urlsplit(site_url)
    site_host = site_parts.netloc.casefold()
    site_prefix = site_parts.path.rstrip("/")
    parsed = urlsplit(target)
    if parsed.netloc and parsed.netloc.casefold() != site_host:
        return None
    if parsed.scheme and parsed.netloc.casefold() != site_host:
        return None

    target_path = unquote(parsed.path).replace("\\", "/")
    if site_prefix and target_path.startswith(site_prefix + "/"):
        target_path = target_path[len(site_prefix) :]
    if not target_path:
        return None
    if target_path.startswith("/"):
        candidate = posixpath.normpath(target_path.lstrip("/"))
    else:
        candidate = posixpath.normpath(
            posixpath.join(posixpath.dirname(normalize_source(source_uri)), target_path)
        )
    if candidate in {".", ".."} or candidate.startswith("../"):
        return None
    candidate = candidate.lstrip("/")

    if candidate in by_source:
        return by_source[candidate]
    if candidate.endswith(".md"):
        return by_route.get(route_key(route_for_source(candidate)))
    if route_key(candidate) in by_route:
        return by_route[route_key(candidate)]

    for possible in (candidate + ".md", candidate.rstrip("/") + "/index.md"):
        if possible in by_source:
            return by_source[possible]

    stem = PurePosixPath(candidate.rstrip("/")).stem.casefold()
    stem_candidates = by_stem.get(stem, [])
    if len(stem_candidates) == 1:
        return stem_candidates[0]
    title_candidates = by_title.get(candidate.strip().casefold(), [])
    return title_candidates[0] if len(title_candidates) == 1 else None


def _wiki_parts(payload: str) -> tuple[str, str | None, str | None]:
    target, separator, alias = payload.partition("|")
    target_path, fragment_separator, fragment = target.partition("#")
    if not fragment_separator and separator and "#" in alias:
        alias, _, fragment = alias.partition("#")
        fragment_separator = "#"
    return target_path.strip(), alias.strip() if separator else None, fragment.strip() if fragment_separator else None


def _fragment_id(fragment: str) -> str:
    fragment = unquote(fragment).strip().casefold()
    fragment = re.sub(r"[^\w\- ]", "", fragment)
    return re.sub(r"\s+", "-", fragment)


def rewrite_wikilinks(
    markdown: str,
    source_uri: str,
    pages: list[GraphPage],
    site_url: str = "",
) -> tuple[str, list[str]]:
    """Convert Obsidian wikilinks to ordinary links outside code blocks."""
    unresolved: list[str] = []
    output: list[str] = []
    inside_fence = False
    fence_char = ""
    fence_size = 0

    def replace_inline(match: re.Match) -> str:
        if match.group("code"):
            return match.group(0)
        payload = match.group("wiki")[2:-2].strip()
        target, alias, fragment = _wiki_parts(payload)
        page = resolve_page_target(pages, source_uri, target, site_url)
        if page is None:
            unresolved.append(target)
            return match.group(0)
        label = alias or page.title
        href = page.url or route_for_source(page.src_uri)
        if fragment:
            href += "#" + _fragment_id(fragment)
        return f"[{label}]({href})"

    for line in markdown.splitlines(keepends=True):
        fence = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence:
            marker = fence.group(1)
            if not inside_fence:
                inside_fence = True
                fence_char = marker[0]
                fence_size = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_size:
                inside_fence = False
            output.append(line)
        elif inside_fence:
            output.append(line)
        else:
            output.append(WIKI_LINK_TOKEN_RE.sub(replace_inline, line))

    return "".join(output), unresolved


def extract_targets(markdown: str) -> list[tuple[str, str]]:
    """Find local-link candidates while ignoring code examples and images."""
    source = INLINE_CODE_RE.sub("", FENCED_CODE_RE.sub("", markdown))
    source = INLINE_MATH_RE.sub("", DISPLAY_MATH_RE.sub("", source))
    targets: list[tuple[str, str]] = []
    reference_definitions = {
        label.strip().casefold(): target.strip()
        for label, target in REFERENCE_DEF_RE.findall(source)
    }

    for match in INLINE_LINK_RE.finditer(source):
        target = match.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        else:
            target = target.split(None, 1)[0]
        targets.append((html.unescape(target), "markdown"))

    for match in REFERENCE_LINK_RE.finditer(source):
        target = reference_definitions.get(match.group(1).strip().casefold())
        if target:
            targets.append((html.unescape(target), "markdown"))

    for match in HTML_LINK_RE.finditer(source):
        targets.append((html.unescape(match.group(1).strip()), "markdown"))

    for match in WIKI_LINK_RE.finditer(source):
        target, _, _ = parse_wikilink(match.group(1).strip())
        targets.append((html.unescape(target), "wikilink"))

    return targets


def build_graph(
    pages: list[GraphPage],
    site_name: str = "Wiki",
    site_url: str = "",
) -> tuple[dict, dict]:
    """Build page-link edges and the folder hierarchy for published pages."""
    pages_by_source: dict[str, GraphPage] = {}
    page_ids: dict[str, str] = {}
    page_routes: dict[str, str] = {}
    page_ids_by_stem: dict[str, list[str]] = {}
    page_ids_by_title: dict[str, list[str]] = {}

    for page in pages:
        source = normalize_source(page.src_uri)
        page_id = f"page:{source}"
        pages_by_source[source] = page
        page_ids[source] = page_id
        page_ids[posixpath.splitext(source)[0]] = page_id
        page_routes[route_key(route_for_source(source))] = page_id
        page_ids_by_stem.setdefault(PurePosixPath(source).stem.casefold(), []).append(page_id)
        page_ids_by_title.setdefault(page.title.strip().casefold(), []).append(page_id)

    site_parts = urlsplit(site_url)
    site_host = site_parts.netloc.casefold()
    site_prefix = site_parts.path.rstrip("/")

    def resolve_target(source_uri: str, target: str) -> str | None:
        target = target.strip()
        if not target or target.startswith("#"):
            return None

        parsed = urlsplit(target)
        if parsed.netloc and parsed.netloc.casefold() != site_host:
            return None
        if parsed.scheme and parsed.netloc.casefold() != site_host:
            return None

        target_path = unquote(parsed.path).replace("\\", "/")
        if site_prefix and target_path.startswith(site_prefix + "/"):
            target_path = target_path[len(site_prefix) :]
        if not target_path:
            return None

        if target_path.startswith("/"):
            candidate = posixpath.normpath(target_path.lstrip("/"))
        else:
            candidate = posixpath.normpath(
                posixpath.join(posixpath.dirname(normalize_source(source_uri)), target_path)
            )
        if candidate == "." or candidate == ".." or candidate.startswith("../"):
            return None
        candidate = candidate.lstrip("/")

        if candidate in page_ids:
            return page_ids[candidate]

        if candidate.endswith(".md"):
            route = route_key(route_for_source(candidate))
            return page_routes.get(route)

        route = route_key(candidate)
        if route in page_routes:
            return page_routes[route]

        for possible in (candidate + ".md", candidate.rstrip("/") + "/index.md"):
            if possible in page_ids:
                return page_ids[possible]

        stem = PurePosixPath(candidate.rstrip("/")).stem.casefold()
        stem_candidates = page_ids_by_stem.get(stem, [])
        if len(stem_candidates) == 1:
            return stem_candidates[0]
        title_candidates = page_ids_by_title.get(candidate.strip().casefold(), [])
        if len(title_candidates) == 1:
            return title_candidates[0]
        return None

    top_level = sorted({source.split("/", 1)[0] for source in pages_by_source})
    category_names = [site_name] + [
        item.upper() if item.casefold() in {"ml", "cs"} else item for item in top_level
    ]
    category_ids = {name: index for index, name in enumerate(category_names)}

    def branch_category(path: str) -> int:
        branch = path.split("/", 1)[0] if path else site_name
        category_name = branch.upper() if branch.casefold() in {"ml", "cs"} else branch
        return category_ids.get(category_name, 0)

    nodes: list[dict] = [
        {
            "id": "directory:/",
            "name": site_name,
            "value": "",
            "kind": "directory",
            "symbolSize": 20,
            "category": 0,
        }
    ]
    for source, page in pages_by_source.items():
        nodes.append(
            {
                "id": page_ids[source],
                "name": page.title,
                "value": page.url or route_for_source(source),
                "kind": "page",
                "symbolSize": 9,
                "category": branch_category(source),
            }
        )

    directory_paths: set[str] = set()
    for source in pages_by_source:
        parent = posixpath.dirname(source)
        while parent:
            directory_paths.add(parent)
            parent = posixpath.dirname(parent)

    for directory in sorted(directory_paths):
        nodes.append(
            {
                "id": f"directory:/{directory}",
                "name": posixpath.basename(directory),
                "value": "",
                "kind": "directory",
                "symbolSize": max(7, 14 - 2 * directory.count("/")),
                "category": branch_category(directory),
            }
        )

    edges: dict[tuple[str, str, str], dict] = {}

    def add_edge(source: str, target: str, kind: str) -> None:
        if source != target:
            edges[(source, target, kind)] = {"source": source, "target": target, "kind": kind}

    # Preserve folder context as a separate, filterable relation.
    for directory in sorted(directory_paths):
        parent = posixpath.dirname(directory)
        parent_id = f"directory:/{parent}" if parent else "directory:/"
        add_edge(parent_id, f"directory:/{directory}", "hierarchy")
    for source in pages_by_source:
        parent = posixpath.dirname(source)
        parent_id = f"directory:/{parent}" if parent else "directory:/"
        add_edge(parent_id, page_ids[source], "hierarchy")

    unresolved: list[dict[str, str]] = []
    for source, page in pages_by_source.items():
        for target, kind in extract_targets(page.markdown):
            target_id = resolve_target(source, target)
            if target_id:
                add_edge(page_ids[source], target_id, kind)
                continue

            parsed = urlsplit(target)
            local_path = parsed.path.lstrip("/")
            if (
                not parsed.scheme
                and not parsed.netloc
                and local_path
                and not local_path.startswith("assets/")
            ):
                unresolved.append({"source": source, "target": target})

    graph = {
        "nodes": nodes,
        "links": [edges[key] for key in sorted(edges)],
        "categories": [{"name": name} for name in category_names],
    }
    counts = {kind: sum(edge["kind"] == kind for edge in graph["links"]) for kind in ("hierarchy", "markdown", "wikilink")}
    stats = {
        "pages": len(pages_by_source),
        "directories": len(directory_paths) + 1,
        "edges": counts,
        "unresolved_internal_links": unresolved,
    }
    return graph, stats


def write_graph(graph: dict, site_dir: Path) -> Path:
    output = site_dir / "assets" / "js" / "graph.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
