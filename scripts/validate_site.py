"""Check built HTML for invalid KaTeX and missing local image assets.

Usage: python scripts/validate_site.py generated

The parser uses the same KaTeX version loaded by the site. Node.js and npm are
required; npm exec keeps the check self-contained and does not add a project
package.json or lockfile.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit

MATH_RE = re.compile(
    r'<(?P<tag>span|div)\b(?=[^>]*\bclass="[^"]*\barithmatex\b[^"]*")[^>]*>'
    r"(?P<body>.*?)</(?P=tag)>",
    re.S,
)
IMAGE_RE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.I)
TEXT_MACRO_RE = re.compile(r"\\text\{([^{}]+)\}")
HIGHLIGHT_RE = re.compile(r'<mark\b[^>]*data-md-highlight[^>]*>(.*?)</mark>', re.S)
KATEX_VERSION = "0.16.9"

NODE_VALIDATOR = r"""
const fs = require('fs');
const path = require('path');
const bins = process.env.PATH.split(path.delimiter);
const bin = bins.find(p => p.includes(`${path.sep}_npx${path.sep}`) && p.endsWith(`${path.sep}node_modules${path.sep}.bin`));
if (!bin) throw new Error('Could not locate npm-exec KaTeX package');
const katex = require(path.join(path.dirname(bin), 'katex'));
const formulas = JSON.parse(fs.readFileSync(0, 'utf8'));
const errors = [];
for (const formula of formulas) {
  try {
    katex.renderToString(formula.tex, {
      displayMode: formula.display,
      strict: 'ignore',
      throwOnError: true
    });
  } catch (error) {
    errors.push({file: formula.file, tex: formula.tex.slice(0, 240), scenario: formula.scenario, error: error.message});
  }
}
process.stdout.write(JSON.stringify({checked: formulas.length, errors}));
"""


def formulas_from_html(site_dir: Path) -> list[dict[str, str | bool]]:
    formulas: list[dict[str, str | bool]] = []
    for html_file in site_dir.rglob("*.html"):
        html = html_file.read_text(encoding="utf-8", errors="replace")
        for match in MATH_RE.finditer(html):
            body = unescape(re.sub(r"<[^>]*>", "", match.group("body"))).strip()
            if body.startswith(r"\(") and body.endswith(r"\)"):
                body = body[2:-2].strip()
            elif body.startswith(r"\[") and body.endswith(r"\]"):
                body = body[2:-2].strip()
            if body:
                source_file = html_file.relative_to(site_dir).as_posix()
                display = match.group("tag") == "div"
                formulas.append({"file": source_file, "display": display, "tex": body, "scenario": "source"})

                # Material's search.highlight decorates matching words in the
                # rendered page. Simulate a hit inside \text{...} and verify
                # the same mark-unwrapping behavior used by katex.js.
                text_macro = TEXT_MACRO_RE.search(body)
                if text_macro:
                    word = re.search(r"[A-Za-z]+", text_macro.group(1))
                    if word:
                        start, end = word.span()
                        content_start = text_macro.start(1)
                        highlighted = (
                            body[: content_start + start]
                            + '<mark data-md-highlight="">'
                            + body[content_start + start : content_start + end]
                            + "</mark>"
                            + body[content_start + end :]
                        )
                        sanitized = HIGHLIGHT_RE.sub(r"\1", highlighted)
                        formulas.append(
                            {
                                "file": source_file,
                                "display": display,
                                "tex": sanitized,
                                "scenario": "search-highlight-inside-text",
                            }
                        )
    return formulas


def missing_images(site_dir: Path) -> list[tuple[str, str]]:
    missing: list[tuple[str, str]] = []
    for html_file in site_dir.rglob("*.html"):
        html = html_file.read_text(encoding="utf-8", errors="replace")
        for match in IMAGE_RE.finditer(html):
            source = unescape(match.group(1).strip())
            parsed = urlsplit(source)
            if parsed.scheme or not parsed.path:
                continue
            asset_path = Path(unquote(parsed.path.lstrip("/")))
            target = site_dir / asset_path if parsed.path.startswith("/") else html_file.parent / asset_path
            if not target.is_file():
                missing.append((html_file.relative_to(site_dir).as_posix(), source))
    return missing


def validate_graph(site_dir: Path) -> tuple[dict | None, list[str]]:
    graph_file = site_dir / "assets" / "js" / "graph.json"
    if not graph_file.is_file():
        return None, [f"Missing graph data: {graph_file.relative_to(site_dir)}"]

    graph = json.loads(graph_file.read_text(encoding="utf-8"))
    errors: list[str] = []
    nodes = graph.get("nodes", [])
    links = graph.get("links", [])
    node_ids = [node.get("id") for node in nodes]
    node_id_set = set(node_ids)
    node_by_id = {node.get("id"): node for node in nodes}
    if len(node_ids) != len(node_id_set):
        errors.append("Graph contains duplicate node IDs.")

    page_urls: set[str] = set()
    for node in nodes:
        if node.get("kind") == "page":
            value = node.get("value", "")
            if not value:
                errors.append(f"Page node has no URL: {node.get('name', node.get('id'))}")
                continue
            route = urlsplit(value).path
            output = site_dir / unquote(route.lstrip("/"))
            if route.endswith("/") or not output.suffix:
                output = output / "index.html"
            if not output.is_file():
                errors.append(f"Graph page URL has no generated page: {value}")
            if route in page_urls:
                errors.append(f"Duplicate graph page URL: {value}")
            page_urls.add(route)

    seen_edges: set[tuple[str, str, str]] = set()
    for edge in links:
        source = edge.get("source")
        target = edge.get("target")
        kind = edge.get("kind")
        if source not in node_id_set or target not in node_id_set:
            errors.append(f"Graph edge references a missing node: {source} -> {target}")
        key = (source, target, kind)
        if key in seen_edges:
            errors.append(f"Duplicate {kind} graph edge: {source} -> {target}")
        seen_edges.add(key)
        if kind not in {"hierarchy", "markdown", "wikilink"}:
            errors.append(f"Unexpected graph edge kind: {kind}")
        if kind in {"markdown", "wikilink"}:
            if node_by_id.get(source, {}).get("kind") != "page" or node_by_id.get(target, {}).get("kind") != "page":
                errors.append(f"Page-link edge must connect page nodes: {source} -> {target}")

    return graph, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", nargs="?", default="generated", type=Path)
    args = parser.parse_args()
    site_dir = args.site_dir.resolve()
    if not site_dir.is_dir():
        parser.error(f"site directory does not exist: {site_dir}")

    formulas = formulas_from_html(site_dir)
    katex_script = Path(__file__).resolve().parents[1] / "content/assets/js/katex.js"
    katex_runtime = katex_script.read_text(encoding="utf-8")
    required_runtime_fragments = (
        ".arithmatex mark[data-md-highlight]",
        "highlight.replaceWith(document.createTextNode(highlight.textContent || \"\"))",
        "removeSearchHighlightsFromMath(root);",
    )
    if any(fragment not in katex_runtime for fragment in required_runtime_fragments):
        print("KaTeX runtime is missing or bypasses search-highlight cleanup for math blocks.")
        return 1
    result = subprocess.run(
        [
            "npm",
            "exec",
            "--yes",
            f"--package=katex@{KATEX_VERSION}",
            "--",
            "node",
            "-e",
            NODE_VALIDATOR,
        ],
        input=json.dumps(formulas),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        return result.returncode

    katex_result = json.loads(result.stdout)
    missing = missing_images(site_dir)
    graph, graph_errors = validate_graph(site_dir)
    print(f"KaTeX formulas checked: {katex_result['checked']} (KaTeX {KATEX_VERSION})")
    print(f"Missing local images: {len(missing)}")
    if graph is not None:
        nodes = graph.get("nodes", [])
        links = graph.get("links", [])
        page_nodes = sum(node.get("kind") == "page" for node in nodes)
        directory_nodes = sum(node.get("kind") == "directory" for node in nodes)
        link_counts = {
            kind: sum(edge.get("kind") == kind for edge in links)
            for kind in ("hierarchy", "markdown", "wikilink")
        }
        print(
            f"Graph checked: {page_nodes} pages, {directory_nodes} directories; "
            f"edges {link_counts}"
        )
    for error in katex_result["errors"]:
        print(f"KaTeX error in {error['file']}: {error['error']}\n  {error['tex']}")
    for html_file, source in missing:
        print(f"Missing image in {html_file}: {source}")
    for error in graph_errors:
        print(f"Graph error: {error}")
    return 1 if katex_result["errors"] or missing or graph_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
