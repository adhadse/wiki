$(function () {
  var sectionIds = $('#TableOfContents:first a');
    $(document).on('scroll', function(){
        sectionIds.each(function(i, e){
            var container = $(this).attr('href');
            var containerOffset = $(container).offset().top;
            var nextContainer = $(sectionIds[i+1]).attr('href')

            if (i != sectionIds.length-1) {
              var containerHeight = $(nextContainer).offset().top;
            } else {
              var containerHeight = $(container).outerHeight() + $(".docs-navigation").offset().top;
            }
            var containerBottom = containerOffset + containerHeight;

            var scrollPosition = $(document).scrollTop();
            if(scrollPosition < containerBottom - 20 && scrollPosition >= containerOffset - 20){
              for (var j = i; j >= 0; j--) {
                $(sectionIds[j]).removeClass('active');
              }
              $(sectionIds[i]).addClass('active');
            } else{
                $(sectionIds[i]).removeClass('active');
            }
        });
    });
});

var suggestions = document.getElementById('suggestions');
var search = document.getElementById('search');

if (search !== null) {
  document.addEventListener('keydown', inputFocus);
}

function inputFocus(e) {
  if (e.ctrlKey && e.key === '/' ) {
    e.preventDefault();
    search.focus();
  }
  if (e.key === 'Escape' ) {
    search.blur();
    suggestions.classList.add('d-none');
  }
}

document.addEventListener('click', function(event) {

  var isClickInsideElement = suggestions.contains(event.target);

  if (!isClickInsideElement) {
    suggestions.classList.add('d-none');
  }

});

/*
Source:
  - https://dev.to/shubhamprakash/trap-focus-using-javascript-6a3
*/

document.addEventListener('keydown',suggestionFocus);

function suggestionFocus(e) {
  const suggestionsHidden = suggestions.classList.contains('d-none');
  if (suggestionsHidden) return;

  const focusableSuggestions= [...suggestions.querySelectorAll('a')];
  if (focusableSuggestions.length === 0) return;

  const index = focusableSuggestions.indexOf(document.activeElement);

  if (e.key === "ArrowUp") {
    e.preventDefault();
    const nextIndex = index > 0 ? index - 1 : 0;
    focusableSuggestions[nextIndex].focus();
  }
  else if (e.key === "ArrowDown") {
    e.preventDefault();
    const nextIndex= index + 1 < focusableSuggestions.length ? index + 1 : index;
    focusableSuggestions[nextIndex].focus();
  }

}

/*
Source:
  - https://github.com/nextapps-de/flexsearch#index-documents-field-search
  - https://raw.githack.com/nextapps-de/flexsearch/master/demo/autocomplete.html
*/

(function(){

  var index = new FlexSearch.Document({
    tokenize: "forward",
    cache: 100,
    document: {
      id: 'id',
      store: [
        "href", "title", "description"
      ],
      index: ["title", "description"]
    }
  });


  // Not yet supported: https://github.com/nextapps-de/flexsearch#complex-documents

  /*
  var docs = [
    {{ range $index, $page := (where .Site.Pages "Section" "docs") -}}
      {
        id: {{ $index }},
        href: "{{ .Permalink }}",
        title: {{ .Title | jsonify }},
        description: {{ .Params.description | jsonify }},
        content: {{ .Content | jsonify }}
      },
    {{ end -}}
  ];
  */

  // https://discourse.gohugo.io/t/range-length-or-last-element/3803/2

  {{ $list := slice }}
  {{- if and (isset .Site.Params.options "searchsectionsindex") (not (eq (len .Site.Params.options.searchSectionsIndex) 0)) }}
  {{- if eq .Site.Params.options.searchSectionsIndex "ALL" }}
  {{- $list = .Site.Pages }}
  {{- else }}
  {{- $list = (where .Site.Pages "Type" "in" .Site.Params.options.searchSectionsIndex) }}
  {{- if (in .Site.Params.options.searchSectionsIndex "HomePage") }}
  {{ $list = $list | append .Site.Home }}
  {{- end }}
  {{- end }}
  {{- else }}
  {{- $list = (where .Site.Pages "Section" "docs") }}
  {{- end }}

  {{ $len := (len $list) -}}
  {{ $last_index := newScratch -}}
  {{ $last_index.Set "value" $len -}}

  {{ range $index, $element := $list -}}
    {{ $RelPermalink := .RelPermalink -}}
    {{ $title := .Title | jsonify -}}
    index.add({
      id: {{ $index }},
      href: "{{ $RelPermalink }}",
      title: {{ $title }},
      {{ with .Description -}}
      description: {{ . | truncate 35 | jsonify }},
      {{ else -}}
      description: {{ .Summary | plainify | truncate 35 |jsonify  }},
      {{ end -}}
    });

    {{ $sections := findRE `(?s)<h[1-3].*?>.*?</h[1-3]>` .Content }}

    {{ range $idx, $section := $sections -}}
      {{ $section_id := replaceRE `\"` "" (index (findRE `\"#([\S]+)\"` $section) 0) }}
      {{ $section_title := replaceRE `>|.<.` "" (index (findRE `>[\S\s]+<a` $section) 0) }}
        index.add({
            id: {{ add ($last_index.Get "value") $idx }},
            href: "{{ $RelPermalink }}{{ $section_id }}",
            title: {{ $title }},
            description: "{{ $section_title | plainify }}",
          });
    {{ end -}}
    {{ $last_index.Add "value" (len $sections) -}}
  {{ end -}}

  search.addEventListener('input', show_results, true);

  function show_results(){
    const maxResult = 5;
    var searchQuery = this.value;
    var results = index.search(searchQuery, {limit: maxResult, enrich: true});

    // flatten results since index.search() returns results for each indexed field
    const flatResults = new Map(); // keyed by href to dedupe results
    for (const result of results.flatMap(r => r.result)) {
      if (flatResults.has(result.doc.href)) continue;
      flatResults.set(result.doc.href, result.doc);
    }

    suggestions.innerHTML = "";
    suggestions.classList.remove('d-none');

    // inform user that no results were found
    if (flatResults.size === 0 && searchQuery) {
      const noResultsMessage = document.createElement('div')
      noResultsMessage.innerHTML = `No results for "<strong>${searchQuery}</strong>"`
      noResultsMessage.classList.add("suggestion__no-results");
      suggestions.appendChild(noResultsMessage);
      return;
    }

    // construct a list of suggestions
    for(const [href, doc] of flatResults) {
        const entry = document.createElement('div');
        suggestions.appendChild(entry);

        const a = document.createElement('a');
        a.href = href;
        entry.appendChild(a);

        const title = document.createElement('span');
        title.textContent = doc.title;
        title.classList.add("suggestion__title");
        a.appendChild(title);

        const description = document.createElement('span');
        description.textContent = doc.description;
        description.classList.add("suggestion__description");
        a.appendChild(description);

        suggestions.appendChild(entry);

        if(suggestions.childElementCount == maxResult) break;
    }
  }
}());
