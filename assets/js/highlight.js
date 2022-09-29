import hljs from 'highlight.js/lib/core';
window.hljs = hljs;
require('highlightjs-line-numbers.js');
import javascript from 'highlight.js/lib/languages/javascript';
import text from 'highlight.js/lib/languages/plaintext';
import json from 'highlight.js/lib/languages/json';
import bash from 'highlight.js/lib/languages/bash';
import xml from 'highlight.js/lib/languages/xml';
import ini from 'highlight.js/lib/languages/ini';
import yaml from 'highlight.js/lib/languages/yaml';
import markdown from 'highlight.js/lib/languages/markdown';
import go from 'highlight.js/lib/languages/go';
import python from 'highlight.js/lib/languages/python';
import cpp from 'highlight.js/lib/languages/cpp';
import c from 'highlight.js/lib/languages/c';
import rust from 'highlight.js/lib/languages/rust';


hljs.registerLanguage('javascript', javascript);
hljs.registerLanguage('text', text);
hljs.registerLanguage('json', json);
hljs.registerLanguage('bash', bash);
hljs.registerLanguage('html', xml);
hljs.registerLanguage('ini', ini);
hljs.registerLanguage('toml', ini);
hljs.registerLanguage('yaml', yaml);
hljs.registerLanguage('markdown', markdown);
hljs.registerLanguage('rust', rust);
hljs.registerLanguage('go', go);
hljs.registerLanguage('python', python);
hljs.registerLanguage('cpp', cpp);
hljs.registerLanguage('c', c);



document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('pre code:not(.language-mermaid)').forEach((block) => {
    hljs.highlightElement(block);
    hljs.initLineNumbersOnLoad();
    var language = block.result.language;
    if (language === undefined) {
      language = '?'
    }
    
    const pills = document.createElement("div");
    pills.className = "pills";
    pills.innerHTML = `
      <label class="language">${language}</label>
       <button class="copy">Copy</button>`;
    block.parentElement.appendChild(pills);
  });
});
