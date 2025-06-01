// function definitions
function draw_graph_sidebar(myChart, global = false) {
  draw_graph(myChart, global);
}

function draw_graph_modal(myChart, global = true) {
  draw_graph(myChart, global);
}

function add_graph_div(params) {
  $(".md-sidebar--secondary").each(function () {
    $(this).find("#graph.graph").remove();
    $(this).contents().append('<div id="graph" class="graph"></div>');
  });
}

function init_graph(params) {
  var myChart = echarts.init(document.getElementById("graph"), null, {
    renderer: "canvas",
    useDirtyRect: false,
  });
  return myChart;
}

function draw_graph(myChart, global = true) {
  var _option = $.extend(true, {}, option);

  // Configure tooltip visibility
  if (!_option.tooltip) {
    // Ensure tooltip object exists
    _option.tooltip = {};
  }
  if (global) {
    // Modal view
    _option.tooltip.show = true;
  } else {
    // Sidebar view
    _option.tooltip.show = false;
  }

  if (!global) {
    _option.series[0].data = graph_nodes();
    _option.series[0].links = graph_links();
  } else {
    // This is for the modal view (global = true)
    // Modify label formatter to show labels only for nodes with an empty value
    if (_option.series && _option.series[0] && _option.series[0].label) {
      _option.series[0].label.formatter = function (params) {
        // params.data corresponds to a node from graph.nodes
        // each node has a 'value' field (which is the URL)
        // and a 'name' field (which is the title)
        if (params.data && params.data.value === "") {
          return params.name; // Show label (node name)
        }
        return ""; // Hide label
      };
      // Ensure show is true, so the formatter can decide visibility for each label
      _option.series[0].label.show = true;
    }
  }
  // draw the graph
  myChart.setOption(_option);

  // add click event for nodes
  myChart.on("click", function (params) {
    if (params.dataType == "node") {
      window.location = params.value;
    }
  });

  // redraw on resize
  window.addEventListener("resize", myChart.resize);
}

function graph_links() {
  // Ensure option and option.series[0].data are loaded before calling this
  if (!option || !option.series || !option.series[0] || !option.series[0].data)
    return [];
  const currentPathNode = option.series[0].data.find(
    (it) => it.value === window.location.pathname
  );
  if (!currentPathNode) return [];
  const id = currentPathNode.id;
  return option.series[0].links.filter(
    (it) => it.source === id || it.target === id
  );
}

function graph_nodes() {
  // Ensure option and option.series[0].data are loaded before calling this
  if (!option || !option.series || !option.series[0] || !option.series[0].data)
    return [];
  const currentPathNode = option.series[0].data.find(
    (it) => it.value === window.location.pathname
  );
  if (!currentPathNode) return [];
  const id = currentPathNode.id;
  const links = option.series[0].links.filter(
    (it) => it.source === id || it.target === id
  );
  const ids = [];
  links.forEach(function (link) {
    ids.push(link.source, link.target);
  });
  return option.series[0].data.filter((it) =>
    [...new Set(ids)].includes(it.id)
  );
}

// global variables for chart instance and options
var myChart;
var option;

document$.subscribe(() => {
  // Dispose previous sidebar chart instance if it exists (e.g., due to page navigation)
  if (
    myChart &&
    typeof myChart.dispose === "function" &&
    !myChart.isDisposed()
  ) {
    myChart.dispose();
  }

  // One-time setup for graph button and its primary listeners
  if ($("#graph_button").length === 0) {
    // Add graph button next to light/dark mode switch if activated, but before search
    $(".md-search").before(
      '<form class="md-header__option"> \
                            <label id="graph_button" class="md-header__button md-icon"> \
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 171 146"> \
                                <path d="M171,100 C171,106.075 166.075,111 160,111 C154.016,111 149.158,106.219 149.014,100.27 L114.105,83.503 C111.564,86.693 108.179,89.18 104.282,90.616 L108.698,124.651 C112.951,126.172 116,130.225 116,135 C116,141.075 111.075,146 105,146 C98.925,146 94,141.075 94,135 C94,131.233 95.896,127.912 98.781,125.93 L94.364,91.896 C82.94,90.82 74,81.206 74,69.5 C74,69.479 74.001,69.46 74.001,69.439 L53.719,64.759 C50.642,70.269 44.76,74 38,74 C36.07,74 34.215,73.689 32.472,73.127 L20.624,90.679 C21.499,92.256 22,94.068 22,96 C22,102.075 17.075,107 11,107 C4.925,107 0,102.075 0,96 C0,89.925 4.925,85 11,85 C11.452,85 11.895,85.035 12.332,85.089 L24.184,67.531 C21.574,64.407 20,60.389 20,56 C20,48.496 24.594,42.07 31.121,39.368 L29.111,21.279 C24.958,19.707 22,15.704 22,11 C22,4.925 26.925,0 33,0 C39.075,0 44,4.925 44,11 C44,14.838 42.031,18.214 39.051,20.182 L41.061,38.279 C49.223,39.681 55.49,46.564 55.95,55.011 L76.245,59.694 C79.889,52.181 87.589,47 96.5,47 C100.902,47 105.006,48.269 108.475,50.455 L131.538,27.391 C131.192,26.322 131,25.184 131,24 C131,17.925 135.925,13 142,13 C148.075,13 153,17.925 153,24 C153,30.075 148.075,35 142,35 C140.816,35 139.678,34.808 138.609,34.461 L115.546,57.525 C117.73,60.994 119,65.098 119,69.5 C119,71.216 118.802,72.884 118.438,74.49 L153.345,91.257 C155.193,89.847 157.495,89 160,89 C166.075,89 171,93.925 171,100"> \
                                </path> \
                              </svg> \
                            </label> \
                          </form>'
    );

    // Palette change listener
    $("#__palette_0, #__palette_1").change(function () {
      if (
        option &&
        myChart &&
        typeof myChart.setOption === "function" &&
        !myChart.isDisposed()
      ) {
        option.backgroundColor = $("body").css("background-color");
        myChart.setOption(option);
      }
    });

    // Graph button click listener (for modal)
    $("#graph_button").on("click", function (e) {
      $("body").css({ overflow: "hidden", position: "fixed" });
      // Dispose current sidebar chart instance before removing its div
      if (
        myChart &&
        typeof myChart.dispose === "function" &&
        !myChart.isDisposed()
      ) {
        myChart.dispose();
      }
      $("#graph").remove(); // Remove previous graph instance (sidebar)
      $(
        '<div id="modal_background"><div id="graph" class="modal_graph"></div></div>'
      ).appendTo("body");

      var modalChart = echarts.init(document.getElementById("graph"), null, {
        renderer: "canvas",
        useDirtyRect: false,
      });

      if (option) {
        draw_graph_modal(modalChart, true); // Draw with all data
      } else {
        $("#graph").html(
          '<p style="text-align:center;">Graph data loading...</p>'
        );
      }

      $("#modal_background").on("click", function (ev) {
        if (ev.target === this) {
          $("body").css({ overflow: "", position: "" });
          // Dispose modal chart instance before removing its elements
          if (
            typeof modalChart !== "undefined" &&
            modalChart &&
            typeof modalChart.dispose === "function" &&
            !modalChart.isDisposed()
          ) {
            modalChart.dispose();
          }
          $("#graph").remove(); // remove the modal graph div
          $("#modal_background").remove();

          // Re-setup sidebar graph
          add_graph_div();
          myChart = init_graph();
          if (option) {
            draw_graph_sidebar(myChart);
          }
        }
      });
    });
  } // End of one-time setup block

  // Sidebar graph setup (runs on each relevant document$.subscribe trigger)
  add_graph_div(); // Idempotent: ensures a clean #graph div in the sidebar
  myChart = init_graph(); // Initializes sidebar chart on the #graph div

  // Load graph data if not already loaded, then draw sidebar graph
  if (!option) {
    myChart.showLoading();
    var scriptSrc = $('script[src*="interactive_graph.js"]').attr("src");
    var graphJsonUrl = "../js/graph.json"; // Default if scriptSrc is not found or parsing fails
    if (scriptSrc) {
      try {
        var scriptUrl = new URL(scriptSrc, window.location.href);
        var jsonUrl = new URL("../js/graph.json", scriptUrl);
        graphJsonUrl = jsonUrl.pathname;
        if (graphJsonUrl.startsWith("./"))
          graphJsonUrl = graphJsonUrl.substring(2);
        if (
          graphJsonUrl.startsWith("/") &&
          graphJsonUrl.length > 1 &&
          graphJsonUrl[1] === "/"
        ) {
          graphJsonUrl = graphJsonUrl.substring(1);
        }
      } catch (e) {
        console.error("Error constructing graph.json URL from script src:", e);
        graphJsonUrl =
          (document.body.getAttribute("data-md-base-url") || "") +
          "assets/js/graph.json";
        if (graphJsonUrl.startsWith("./"))
          graphJsonUrl = graphJsonUrl.substring(2);
        if (
          graphJsonUrl.startsWith("/") &&
          graphJsonUrl.length > 1 &&
          graphJsonUrl[1] === "/"
        ) {
          graphJsonUrl = graphJsonUrl.substring(1);
        }
      }
    }

    $.getJSON(graphJsonUrl, function (graph) {
      if (
        myChart &&
        typeof myChart.hideLoading === "function" &&
        !myChart.isDisposed()
      ) {
        myChart.hideLoading();
      }

      graph.nodes.forEach(function (node) {
        node.symbolSize += 5;
        node.name = node.name.split(" •")[0];
      });
      graph.links.forEach(function (link) {
        link.source = link.source.split(" •")[0];
        link.target = link.target.split(" •")[0];
      });

      option = {
        tooltip: { show: false },
        legend: [
          /* categories not supported yet */
        ],
        darkMode: "auto",
        backgroundColor: $("body").css("background-color"),
        animationDuration: 1500,
        animationEasingUpdate: "quinticInOut",
        tooltip: {},
        color: [
          '#3EECAC', // A bright mint green (like Valjean)
          '#EEA236', // An orange (like Marius)  // for leaf nodes
          '#5470C6', // A strong blue (could be used for a new category)
          '#9A60B4', // A purple (like Thenardier/Javert)
          '#FC8452', // A softer orange/coral
          '#73C0DE', // A sky blue
          '#DA70D6', // Orchid/Magenta (similar to Gavroche's cluster)
        ],  
        series: [
          {
            name: "Interactive Graph",
            type: "graph",
            layout: "force",
            data: graph.nodes,
            links: graph.links,
            categories: graph.categories,
            zoom: 2,
            roam: true,
            draggable: true,
            label: { show: true, position: "right", formatter: "{b}" },
            emphasis: { focus: "adjacency", label: { fontWeight: "bold" } },
            labelLayout: { hideOverlap: false },
            scaleLimit: { min: 0.5, max: 5 },
            lineStyle: { color: "source", curveness: 0 },
            emphasis: {
              focus: "adjacency",
              lineStyle: {
                width: 10,
              },
            },
          },
        ],
      };
      // Draw sidebar graph with newly loaded options
      if (
        myChart &&
        typeof myChart.setOption === "function" &&
        !myChart.isDisposed()
      ) {
        draw_graph_sidebar(myChart);
      }
    }).fail(function (jqXHR, textStatus, errorThrown) {
      console.error("Failed to load graph.json:", textStatus, errorThrown);
      console.error("Attempted URL:", graphJsonUrl);
      if (
        myChart &&
        typeof myChart.hideLoading === "function" &&
        !myChart.isDisposed()
      ) {
        myChart.hideLoading();
      }
      $("#graph").html(
        '<p style="color:red;text-align:center;">Error loading graph data. Check console.</p>'
      );
    });
  } else {
    // If options are already loaded (e.g., page navigation), draw sidebar graph for current page
    if (
      myChart &&
      typeof myChart.setOption === "function" &&
      !myChart.isDisposed()
    ) {
      draw_graph_sidebar(myChart);
    }
  }
});
