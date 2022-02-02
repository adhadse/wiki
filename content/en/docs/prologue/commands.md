---
title: "Commands"
description: "Doks comes with commands for common tasks."
lead: "Doks comes with commands for common tasks."
date: 2020-10-13T15:21:01+02:00
lastmod: 2020-10-13T15:21:01+02:00
draft: false
images: []
menu:
  docs:
    parent: "prologue"
weight: 130
toc: true
---

## create

Create new content for your site:

```bash
npm run create [path] [flags]
```

See also the Hugo docs: [hugo new](https://gohugo.io/commands/hugo_new/).

## lint

Check scripts, styles, and markdown for errors:

```bash
npm run lint
```

### scripts

Check scripts for errors:

```bash
npm run lint:scripts [-- --fix]
```

### styles

Check styles for errors:

```bash
npm run lint:styles [-- --fix]
```

### markdown

Check markdown for errors:

```bash
npm run lint:markdown [-- --fix]
```

## clean

Delete temporary directories:

```bash
npm run clean
```

## start

Start local development server:

```bash
npm run start
```

## build

Build production website:

```bash
npm run build
```

### functions

Build Lambda functions:

```bash
npm run build:functions
```

### preview

Build production website including draft and future content:

```bash
npm run build:preview
```
--- 
# Components

## Code blocks
```javascript
function highlight(obj){
  var orig = obj.style.color;
  obj.style.color = " #00FF00";
  setTimeout(function(){
       obj.style.background = "#454444";
  }, 3000);
}
```

```python
from abc import abstractmethod
 
# Our interface for class
class CircleInterface:
    @abstractmehod
    def draw_circle(self):
        pass
```
## Katex

This is an example of inline katex $\frac{x}{y}$ with `$\frac{x}{y}$`. 

This is an example of math block of katex.

```markdown
$$
\sin^2 + \cos^2 = 1
$$
```

$$
\sin^2 + \cos^2 = 1
$$

## Tabs
Tabs can be created using `tabs` shortcode passed with uniqueid and `tab` shortcode containing tab content.
{{< tabs "uniqueid" >}}
{{< tab "MacOS" >}} ### MacOS Content 
  Add a default page, documentation page, blog post or contributor page. Customize the homepage and 404 page.  {{< /tab >}}
{{< tab "Linux" >}} ### Linux Content 

{{< /tab >}}
{{< tab "Windows" >}}  
  A sample content to check `code` in tabs.
```python 
def num(l):
  for i in l:
    print(i)
```
$$
\sin^2 + \cos^2 = 1
$$
{{< /tab >}}
{{< /tabs >}}

## Lists
Ordered List 

1. first
2. second
3. third

Unordered List 

- first
- second
- third

Check item

- [X] checked
- [ ] unchecked
- [ ] onemore unchecked

## Panel
Panel can be created using `panel` shortcode.
{{< panel title="What is panel?" >}} 
### A panel is a collapsible section
This is a collapsible panel
{{< /panel >}}

Panel can be by default remain expanded, by passing `collapsed="false"` default is `true`. 
{{< panel title="Code in panel" collapsed="false" >}} 
```html
<div class="accordion-item">
  <div class="card-body">
    Text to display
  </div>
</div>
```
{{< /panel >}}


## Alerts
Alert can be created using shortcode `alert` and passing `type="type-name"`. 

If `type` is not provided then `"primary"` is default.
{{< alert title="A Primary alert">}}
Primary alert with `type="primary"`
{{< /alert >}}

{{< alert type="success" title="A Sucess alert">}}
Sucess alert with `type="success"`
{{< /alert >}}

{{< alert type="danger" title="A Danger alert" >}}
Danger alert with `type="danger"`
{{< /alert >}}

{{< alert type="warning" title="A Warning alert" >}}
Warning alert with `type="warning"`
{{< /alert >}}

{{< alert type="secondary" title="A Secondary alert" >}}
Secondary alert with `type="secondary"`. Can have [link](https://wikipedia.com)
{{< /alert >}}

{{< alert type="secondary" >}}
Secondary alert with `type="secondary"` with no title. The use of alert is 
to help reader guide on some of the most important points or make him aware.
{{< /alert >}}

## Tables 
Tables in markdown.
| Heading 1 📝 | Heading 2🤟 | Heading 3 🎋|
| --- | --- | --- |
| item 1 😶‍🌫️| item 2 | item 3|
| item 3 | $\alpha = \beta$ | `def` |

## File Download 
File download button using `file` shortcode with `link` argument.
{{< file link="/videos/flower.mp4" >}}

File Download button with custom text.

{{< file link="/files/help.txt" title="Django manage.py commands">}}

## Reference Link 
Reference Link can be used to refer to other pages in docs using `ref` shortcode.
{{< ref link="/docs/prologue/quick-start.md">}}

Reference Link can also be passed with custom text using `title` argument. 
{{< ref link="/docs/prologue/introduction.md" title="Let's Begin">}}

With Custom icon `:icon-shortcode:` using `icon` argument. Check [emjoi cheat sheet](https://www.webfx.com/tools/emoji-cheat-sheet/) for more.
{{< ref link="/docs/prologue/commands.md" icon=":heart:" >}}

## Plain Link to external site 
Link button can be created using `link` shortcode.
{{< link link="https://gohugo.io/functions/urls.parse/" title="Hugo Url parse function" >}}

Can be passed with custom icon with argument `icon`.
{{< link link="https://colab.research.google.com/github/adhadse/ColabRepo/blob/master/pydata/Ch%205%20Getting%20Started%20with%20Pandas.ipynb" title="Ch 5 Getting started with pandas" icon=":page_facing_up:">}}

Pass a `target` argument to change the opened link target, default is `_blank`. This is an example when `target="_self"`.
{{< link link="https://www.w3schools.com/tags/att_a_target.asp" title="Attribute a Target" target="_self">}}

