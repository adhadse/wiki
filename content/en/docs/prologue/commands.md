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
```js
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

This is an example of inline katex $\frac{x}{y}$ with `inline code`. 

This is an example of math block of katex.

$$
\sin^2 + \cos^2 = 1
$$

## Tabs

{{< tabs "uniqueid" >}}
{{< tab "MacOS" >}} ### MacOS Content 
  Add a default page, documentation page, blog post or contributor page. Customize the homepage and 404 page.  {{< /tab >}}
{{< tab "Linux" >}} ### Linux Content {{< /tab >}}
{{< tab "Windows" >}} ### Windows Content {{< /tab >}}
{{< /tabs >}}

## Lists
Ordered List 

1. first
2. second
3. third

