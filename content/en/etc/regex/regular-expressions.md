---
title: "Regular Expressions"
description: "Regular expression is a sequence of characters that specifies a search pattern in text."
lead: ""
date: 2022-06-19T14:41:39+01:00
lastmod: 2022-06-19T14:41:39+01:00
draft: false
images: []
type: docs
menu:
  etc: 
    parent: "regex"
weight: 200
toc: false
---

| | Description |
| --- | --- |
| `^` | Matches the beginning of line |
| `$` | Matches the end of line|
| `.` | Mathes any character |
| `\s` | Matches whitespace; equivalent to `[\t\n\r\f\v]`|
| `\S` | Matches any NON-Whitespace; equivalent to `[^\t\n\r\f\v]`|
| `*` | Zero or more time; Repeats a character |
| `*?` | Zero or more times; NON-GREEDY; Repeats a character |
| `+` | One or More times; Repeats a character |
| `+?` | One or More times; NON-GREEDY; Repeats a character |
| `[aeiou]` | Matches a single character in the listed set |
| `[^XYZ]` | Matches a single character NOT in the listed set |
| `[a-z0-9]` | A set of character or an include range|
| `(` | Indicates where the string extraction starts |
| `)` | Indicates where the string extraction ends |
| `a\|b` | matches either a or b, a and b are string |
| `\` | Escape character for special characters (`\t`, `\n`, `\b`) |
| `\b` | Matches word boundary |
| `\d` | Matches single digit; equivalent to `[0-9]` |
| `\w` | Alphanumeric character; `[a-zA-Z0-9_]` |
| `\W` | NON-Alphanumeric character; `[^a-zA-Z0-9_]`|
| `?` | Matches zero or One occurances|
| `{n}` | **Exactly** `n` repetitions, `n>=0` |
| `{n,}` | **Atleast** `n` repeatitions |
| `{,n}` | **Atmost** `n` repeatitions |
| `{m,n}` | Atleast `m` times and atmost `n` repeatitions|
