const mathRenderOptions = {
  delimiters: [
    {left: '$$', right: '$$', display: true},
    {left: '$', right: '$', display: false},
    {left: '\\(', right: '\\)', display: false},
    {left: '\\[', right: '\\]', display: true},
  ],
};

function removeSearchHighlightsFromMath(root) {
  const highlights = root.querySelectorAll(
    ".arithmatex mark[data-md-highlight]",
  );
  for (const highlight of highlights) {
    highlight.replaceWith(document.createTextNode(highlight.textContent || ""));
  }
  return highlights.length > 0;
}

function renderPageMath(root) {
  removeSearchHighlightsFromMath(root);
  renderMathInElement(root, mathRenderOptions);
}

document$.subscribe(({ body }) => {
  renderPageMath(body || document.body);
});

// Material search.highlight can add <mark> nodes after page rendering. Remove
// them from math blocks and retry typesetting so those marks can't split TeX.
const mathHighlightObserver = new MutationObserver((mutations) => {
  const mathHighlightAdded = mutations.some((mutation) =>
    [...mutation.addedNodes].some(
      (node) =>
        node instanceof Element &&
        (node.matches("mark[data-md-highlight]") ||
          node.querySelector("mark[data-md-highlight]")) &&
        node.closest(".arithmatex"),
    ),
  );

  if (mathHighlightAdded) renderPageMath(document.body);
});

mathHighlightObserver.observe(document.body, {childList: true, subtree: true});
