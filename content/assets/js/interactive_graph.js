const graphColors = [
  "#3eecac",
  "#eea236",
  "#5470c6",
  "#9a60b4",
  "#fc8452",
  "#73c0de",
  "#da70d6",
];

let graphDataPromise;
let graphData;
let sidebarChart;
let modalChart;
let modalElement;
let focusBeforeModal;
let oldBodyOverflow = "";
let sidebarRenderId = 0;
const chartObservers = new WeakMap();
const chartResizeHandlers = new WeakMap();

function normalizeRoute(value) {
  try {
    let pathname = new URL(value, window.location.origin).pathname;
    pathname = pathname.replace(/\/index\.html$/, "/");
    return pathname.endsWith("/") ? pathname : `${pathname}/`;
  } catch {
    return value;
  }
}

function activePageId(data = graphData) {
  if (!data) return null;
  const route = normalizeRoute(window.location.pathname);
  return data.nodes.find(
    (node) => node.kind === "page" && normalizeRoute(node.value) === route,
  )?.id;
}

function pageForNode(node, data) {
  if (!node) return null;
  if (node.kind === "page") return node.value ? node : null;
  if (node.kind !== "directory") return null;

  const directoryRoute = node.id.replace(/^directory:/, "");
  return data.nodes.find(
    (candidate) =>
      candidate.kind === "page" &&
      normalizeRoute(candidate.value) === normalizeRoute(directoryRoute),
  ) || null;
}

function graphJsonUrl() {
  const script = [...document.scripts].find((item) =>
    item.src.includes("interactive_graph.js"),
  );
  if (script) return new URL("../js/graph.json", script.src).toString();

  const base = document.body.getAttribute("data-md-base-url") || "/";
  return new URL(`${base}assets/js/graph.json`, window.location.href).toString();
}

function loadGraphData() {
  if (!graphDataPromise) {
    graphDataPromise = fetch(graphJsonUrl())
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then((data) => {
        graphData = data;
        return data;
      })
      .catch((error) => {
        graphDataPromise = null;
        throw error;
      });
  }
  return graphDataPromise;
}

function ensureGraphButton() {
  if (document.getElementById("graph_button")) return;
  const search = document.querySelector(".md-search");
  const header = document.querySelector(".md-header__inner");
  const button = document.createElement("button");
  button.type = "button";
  button.id = "graph_button";
  button.className = "md-header__button md-icon graph-button";
  button.setAttribute("aria-label", "Open site graph");
  button.setAttribute("aria-haspopup", "dialog");
  button.title = "Open site graph";
  button.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3a3 3 0 0 0-2.83 2H7a3 3 0 0 0-3 3v1.17a3 3 0 1 0 2 0V8a1 1 0 0 1 1-1h2.17a3 3 0 0 0 5.66 0H17a1 1 0 0 1 1 1v1.17a3 3 0 1 0 2 0V8a3 3 0 0 0-3-3h-2.17A3 3 0 0 0 12 3Zm0 2a1 1 0 1 1 0 2 1 1 0 0 1 0-2ZM5 11a1 1 0 1 1 0 2 1 1 0 0 1 0-2Zm14 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2ZM11 10v3.17a3 3 0 1 0 2 0V10h-2Zm1 5a1 1 0 1 1 0 2 1 1 0 0 1 0-2Z"/>
    </svg>`;
  button.addEventListener("click", openGraphModal);

  if (search) search.before(button);
  else header?.append(button);
}

function ensureSidebarGraph() {
  const sidebar = document.querySelector(".md-sidebar--secondary");
  if (!sidebar) return null;

  const host = sidebar.querySelector(".md-sidebar__inner") || sidebar;
  let container = host.querySelector("[data-wiki-graph-sidebar]");
  if (!container) container = sidebar.querySelector("[data-wiki-graph-sidebar]");
  if (!container) {
    container = document.createElement("div");
    container.id = "graph";
    container.className = "graph";
    container.dataset.wikiGraphSidebar = "true";
    container.setAttribute("role", "img");
    container.setAttribute("aria-label", "Pages linked to this page");
  }
  const toc = host.querySelector(".md-nav--secondary");
  if (container.parentElement !== host || (toc && container.nextElementSibling !== toc)) {
    host.insertBefore(container, toc || host.firstChild);
  }
  return container;
}

function disposeChart(chart) {
  if (!chart || chart.isDisposed()) return;
  chart.off("click");
  chartObservers.get(chart)?.disconnect();
  chartObservers.delete(chart);
  const resizeHandler = chartResizeHandlers.get(chart);
  if (resizeHandler) window.removeEventListener("resize", resizeHandler);
  chartResizeHandlers.delete(chart);
  chart.dispose();
}

function observeChartResize(chart) {
  const element = chart.getDom();
  if (window.ResizeObserver) {
    const observer = new ResizeObserver(() => {
      if (!chart.isDisposed()) chart.resize();
    });
    observer.observe(element);
    chartObservers.set(chart, observer);
    return;
  }

  const resizeHandler = () => {
    if (!chart.isDisposed()) chart.resize();
  };
  window.addEventListener("resize", resizeHandler);
  chartResizeHandlers.set(chart, resizeHandler);
}

function currentNeighborhood(data) {
  const selectedId = activePageId(data);
  if (!selectedId) return {nodes: [], links: [], selectedId: null};

  const links = data.links.filter(
    (edge) => edge.source === selectedId || edge.target === selectedId,
  );
  const ids = new Set([selectedId]);
  for (const edge of links) {
    ids.add(edge.source);
    ids.add(edge.target);
  }
  return {
    nodes: data.nodes.filter((node) => ids.has(node.id)),
    links,
    selectedId,
  };
}

function visibleGlobalGraph(data) {
  const showHierarchy =
    modalElement?.querySelector("#graph-filter-hierarchy")?.checked ?? true;
  const showPageLinks =
    modalElement?.querySelector("#graph-filter-page-links")?.checked ?? true;
  const links = data.links.filter((edge) =>
    edge.kind === "hierarchy" ? showHierarchy : showPageLinks,
  );

  if (showHierarchy && showPageLinks) {
    return {nodes: data.nodes, links, selectedId: activePageId(data)};
  }

  const ids = new Set();
  for (const edge of links) {
    ids.add(edge.source);
    ids.add(edge.target);
  }
  const selectedId = activePageId(data);
  if (selectedId) ids.add(selectedId);
  return {
    nodes: data.nodes.filter((node) => ids.has(node.id)),
    links,
    selectedId,
  };
}

function edgeStyle(kind) {
  if (kind === "hierarchy") {
    return {color: "rgba(150, 160, 175, 0.42)", width: 1, type: "dashed"};
  }
  if (kind === "wikilink") {
    return {color: "#3eecac", width: 1.8, type: "solid"};
  }
  return {color: "#73a2ff", width: 1.6, type: "solid"};
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => {
    const entities = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"};
    return entities[char];
  });
}

function makeChartOptions(data, global) {
  const {nodes, links, selectedId} = global
    ? visibleGlobalGraph(data)
    : currentNeighborhood(data);
  const visibleIds = new Set(nodes.map((node) => node.id));
  const seriesData = nodes.map((node) => ({
    ...node,
    symbol: node.kind === "directory" ? "roundRect" : "circle",
    itemStyle: node.id === selectedId ? {borderColor: "#fff", borderWidth: 2} : undefined,
  }));
  const seriesLinks = links
    .filter((edge) => visibleIds.has(edge.source) && visibleIds.has(edge.target))
    .map((edge) => ({...edge, lineStyle: edgeStyle(edge.kind)}));

  return {
    backgroundColor: getComputedStyle(document.body).backgroundColor,
    animationDuration: global ? 900 : 400,
    animationEasingUpdate: "cubicOut",
    color: graphColors,
    tooltip: {
      show: global,
      formatter(params) {
        if (params.dataType === "edge") {
          const label = params.data.kind === "hierarchy" ? "Folder hierarchy" : "Page link";
          return `<strong>${escapeHtml(label)}</strong>`;
        }
        const node = params.data;
        const kind = node.kind === "directory" ? "Section" : "Page";
        return `<strong>${escapeHtml(kind)}:</strong> ${escapeHtml(node.name)}`;
      },
    },
    series: [
      {
        type: "graph",
        layout: "force",
        data: seriesData,
        links: seriesLinks,
        categories: data.categories,
        force: {
          repulsion: global ? 260 : 110,
          edgeLength: global ? [70, 125] : [45, 75],
          gravity: 0.08,
          friction: 0.6,
        },
        zoom: global ? 1 : 1.6,
        roam: true,
        draggable: true,
        scaleLimit: {min: 0.35, max: 5},
        label: {
          show: true,
          position: "right",
          formatter(params) {
            const node = params.data;
            return !global || node.kind === "directory" || node.id === selectedId
              ? node.name
              : "";
          },
        },
        emphasis: {
          focus: "adjacency",
          label: {show: true, fontWeight: "bold"},
          lineStyle: {width: 2.5, opacity: 1},
        },
        labelLayout: {hideOverlap: global},
        lineStyle: {opacity: 0.8, curveness: 0.08},
      },
    ],
  };
}

function createChart(container, data, global) {
  if (!container || !window.echarts) return null;
  const chart = window.echarts.init(container, null, {
    renderer: "canvas",
    useDirtyRect: true,
  });
  chart.setOption(makeChartOptions(data, global), true);
  chart.on("click", (params) => {
    if (params.dataType !== "node") return;
    const page = pageForNode(params.data, data);
    if (page) window.location.assign(new URL(page.value, window.location.origin).href);
  });
  chart.on("mouseover", (params) => {
    chart.getDom().style.cursor =
      params.dataType === "node" && pageForNode(params.data, data)
        ? "pointer"
        : "default";
  });
  chart.on("mouseout", () => {
    chart.getDom().style.cursor = "default";
  });
  observeChartResize(chart);
  return chart;
}

async function renderSidebar() {
  const renderId = ++sidebarRenderId;
  disposeChart(sidebarChart);
  sidebarChart = null;

  const container = ensureSidebarGraph();
  if (!container) return;
  container.replaceChildren();

  try {
    const data = await loadGraphData();
    if (renderId !== sidebarRenderId || !container.isConnected) return;
    if (!activePageId(data)) {
      container.hidden = true;
      return;
    }
    container.hidden = false;
    sidebarChart = createChart(container, data, false);
  } catch (error) {
    if (renderId === sidebarRenderId && container.isConnected) {
      container.textContent = "Graph data is unavailable.";
      console.error("Failed to load page graph:", error);
    }
  }
}

function handleModalKeydown(event) {
  if (event.key === "Escape") closeGraphModal();
}

function closeGraphModal() {
  if (!modalElement) return;
  disposeChart(modalChart);
  modalChart = null;
  modalElement.remove();
  modalElement = null;
  document.body.style.overflow = oldBodyOverflow;
  document.removeEventListener("keydown", handleModalKeydown);
  focusBeforeModal?.focus();
  focusBeforeModal = null;
  renderSidebar();
}

async function renderModalGraph() {
  if (!modalElement) return;
  const container = modalElement.querySelector("#graph");
  try {
    const data = await loadGraphData();
    if (!modalElement || !container?.isConnected) return;
    disposeChart(modalChart);
    modalChart = createChart(container, data, true);
  } catch (error) {
    if (container?.isConnected) {
      container.textContent = "Graph data is unavailable.";
      console.error("Failed to load site graph:", error);
    }
  }
}

function openGraphModal() {
  if (modalElement) return;
  focusBeforeModal = document.activeElement;
  oldBodyOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";
  disposeChart(sidebarChart);
  sidebarChart = null;
  document.getElementById("graph")?.remove();

  modalElement = document.createElement("div");
  modalElement.id = "modal_background";
  modalElement.className = "graph-modal-overlay";
  modalElement.setAttribute("role", "presentation");
  modalElement.innerHTML = `
    <section class="graph-modal" role="dialog" aria-modal="true" aria-labelledby="graph-modal-title">
      <header class="graph-modal__toolbar">
        <h2 id="graph-modal-title">Site graph</h2>
        <div class="graph-modal__legend" aria-label="Graph relationship legend">
          <span><i class="graph-legend__line graph-legend__line--page"></i> Page links</span>
          <span><i class="graph-legend__line graph-legend__line--folder"></i> Folder hierarchy</span>
        </div>
        <label class="graph-modal__filter"><input id="graph-filter-page-links" type="checkbox" checked> Page links</label>
        <label class="graph-modal__filter"><input id="graph-filter-hierarchy" type="checkbox" checked> Folders</label>
        <button type="button" class="graph-modal__close" aria-label="Close site graph" title="Close site graph">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M18.3 5.71 17 4.4l-5 5-5-5-1.3 1.31 5 5-5 5L7 17l5-5 5 5 1.3-1.29-5-5z"/>
          </svg>
        </button>
      </header>
      <div id="graph" class="modal_graph" role="application" aria-label="Interactive site graph"></div>
    </section>`;
  modalElement.addEventListener("click", (event) => {
    if (event.target === modalElement) closeGraphModal();
  });
  modalElement.querySelector(".graph-modal__close").addEventListener("click", closeGraphModal);
  for (const filter of modalElement.querySelectorAll(".graph-modal__filter input")) {
    filter.addEventListener("change", renderModalGraph);
  }
  document.addEventListener("keydown", handleModalKeydown);
  document.body.append(modalElement);
  modalElement.querySelector(".graph-modal__close").focus();
  renderModalGraph();
}

function updateChartBackgrounds() {
  const backgroundColor = getComputedStyle(document.body).backgroundColor;
  for (const chart of [sidebarChart, modalChart]) {
    if (chart && !chart.isDisposed()) chart.setOption({backgroundColor});
  }
}

function installGraphButton() {
  if (document.getElementById("graph_button")) return;
  const button = document.createElement("button");
  button.type = "button";
  button.id = "graph_button";
  button.className = "md-header__button md-icon graph-button";
  button.setAttribute("aria-label", "Open site graph");
  button.setAttribute("aria-haspopup", "dialog");
  button.title = "Open site graph";
  button.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3a3 3 0 0 0-2.83 2H7a3 3 0 0 0-3 3v1.17a3 3 0 1 0 2 0V8a1 1 0 0 1 1-1h2.17a3 3 0 0 0 5.66 0H17a1 1 0 0 1 1 1v1.17a3 3 0 1 0 2 0V8a3 3 0 0 0-3-3h-2.17A3 3 0 0 0 12 3Zm0 2a1 1 0 1 1 0 2 1 1 0 0 1 0-2ZM5 11a1 1 0 1 1 0 2 1 1 0 0 1 0-2Zm14 0a1 1 0 1 1 0 2 1 1 0 0 1 0-2ZM11 10v3.17a3 3 0 1 0 2 0V10h-2Zm1 5a1 1 0 1 1 0 2 1 1 0 0 1 0-2Z"/>
    </svg>`;
  button.addEventListener("click", openGraphModal);
  const search = document.querySelector(".md-search");
  const header = document.querySelector(".md-header__inner");
  if (search) search.before(button);
  else header?.append(button);
}

document$.subscribe(() => {
  if (modalElement) closeGraphModal();
  installGraphButton();
  renderSidebar();
  updateChartBackgrounds();
});

const themeObserver = new MutationObserver(updateChartBackgrounds);
themeObserver.observe(document.body, {
  attributes: true,
  attributeFilter: ["data-md-color-scheme", "data-md-color-primary", "data-md-color-accent"],
});
