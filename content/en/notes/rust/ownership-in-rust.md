---
title: "Ownership in Rust"
description: ""
lead: ""
date: 2022-09-20T07:57:56+01:00
lastmod: 2022-09-20T07:57:56+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 4
toc: true
---

## Understanding ownnership
Ownernship model is a way to manage memory in Rust. To understand why we need this model, we need to first understand the typical way programming languages manages memory:

|                    | Pros | Cons  |
| ---                | ---  | ---   |
| Garbage collection | <ul><li>Error free*</li><li>Faster write time</li></ul> | <ul><li>No control over memory</li><li>Slower and unpredictable runtime performance</li><li>Larger program size</li></ul> |
| Manural memory management | <ul><li>Control over memory</li><li>Faster runtime</li><li>Smaller program size</li></ul> | <ul><li>Error prone</li><li>Slower write time</li></ul>|
| Ownership model | <ul><li>Control over memory</li><li>Error free*</li><li>Faster runtime</li><li>Smaller program size</li></ul> | <ul><li>Slower write time. Learning curve (fighting with the borrow checker)</li></ul>|