# Regular Expressions


Use either of these to formulate your regex expression. Both are Open Source.

[:material-link: Regexr](https://regexr.com/){ .md-button }
[:material-link: Regex101](https://regex101.com/">}}){ .md-button }


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
| `a\|b` | matches either a or b, a and b are string matching pattern |
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

## Regex Lookaround
{{< link title="Regex Lookaround" link="https://stackoverflow.com/questions/2973436/regex-lookahead-lookbehind-and-atomic-groups" >}}
- Look ahead positive `(?=)`

   `A(?=B)` find expression A where expression B follows)
- Look ahead negative `(?!)`

  `A(?!B) find expression A where expression B does not follow
- Look behind positive `(?<=)`

  `(?<=B)A` find expression A where expression B precesed
- Look behind negative `(?<!)
  `(?<!B)A find expression A where expression B does not precede
