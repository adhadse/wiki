---
title: "Pattern Syntax in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:26+01:00
lastmod: 2022-09-20T07:58:26+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 30
toc: true
---

All valid syntax to use with pattern matching.

{{< link title="Pattern Syntax" link="https://doc.rust-lang.org/stable/book/ch18-03-pattern-syntax.html" >}}

## Matching Literals
This pattern is useful when we want our code to take action when it receives a concrete value.

```rust
fn main() {
    let x = 1;

    match x {
        1 => println!("one"),
        2 => println!("two"),
        3 => println!("three"),
        _ => println!("anything"),
    }
}
```

## Matching Named Variables
Second branch is using named variable pattern to match other variable shadowing any variable outside of match block.

```rust
fn main() {
    let x = Some(5);
    let y = 10;
    
    match x {
        Some(50) => println!("Got 50"),
        Some(y) => println!("Matched, y = {:?}", y),
        _ => println!("Default case, x = {:?}", x).
    }
}
```

## Multiple patterns

```rust
fn main() {
    let x = 1;

    match x {
        1 | 2 => println!("one or two"), // using OR operator |
        2 => println!("three"),
        3 | 4 | 5 => println!("greater than 2 or equal to 5"),
        _ => println!("anything"),
    }
}
```

## Matching Ranges of Values
The range operator only works on numeric values and characters.

```rust
fn main() {
    let x = 5;

    match x {
        1..=5 => println!("one through five"),
        _ => println!("something else"),
    }

    let x = 'c';

    match x {
        'a'..='j' => println!("early ASCII letter"),
        'k'..='z' => println!("late ASCII letter"),
        _ => println!("something else"),
    }
}
```

## Destructuring to Break Apart Values

### Destructuring structs
We deconstruct `p` a `Point` instance to create `a` and `b`.

`a` is going to be mapped to whatever values contained in `x` and `b` to `y`.
 
```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    let p = Point { x: 0, y: 7};

    let point { x: a, y: b} = p;
    assert_eq!(0, a);
    assert_eq!(7, b);
}
```

However it's common to have variables inside of a pattern match the field names, so:

```rust
let point { x, y } = p;
assert_eq!(0, x);
assert_eq!(7, y);
```
---

When destructuring a struct we can use named variables and literals.

```rust
fn main() {
    let p = Point { x: 0, y: 7};

    match p {
        Point { x, y: 0 } => {    // `y` must be zero
            println!("On the x axis at {}", x)
        },
        Point { x: 0, y} => {     // `x` must be zero
            println!("On the y axis at {}", y)
        },
        Point { x, y } => {
            println!("On neither axis: ({}, {})", x, y)
        }
    }
}
```

### Destructuring Enums

```rust
enum Message {
    Quit,                          // unit like variant 
    Move { x: i32, y: i32},        // struct variant
    Write(String),                 // tuple variant called `Write`
    ChangeColor(i32, i32, i32),    // tuple variant with 3 values called `ChangeColor`
}

fn main() {
    let msg = Message::ChangeColor(0, 160, 255);

    match msg {
        Message::Quit => {
            // a semicolon isn't required if there is only one expression
            println!("Quit");
        }
        Message::Move { x, y } => {
            println!("Move to x: {} y: {}", x, y)
        }
        Message::Write(text) => {
            println!("Text message: {}", text)
        }
        Message::ChangeColor(r, g, b) => {
            println!("Change color: red {}, green {}, and blue {}", r, g, b)
        }
    }
}
```

### Destructuring nested structs and Enums

```rust
enum Color {
    Rgb(i32, i32, i32),
    Hsv(i32, i32, i32),
}

enum Message {
    Quit,                          // unit like variant 
    Move { x: i32, y: i32},        // struct variant
    Write(String),                 // tuple variant called `Write`
    ChangeColor(Color),            // tuple variant with 3 values called `ChangeColor`
}

fn main() {
    let msg = Message::ChangeColor(
        Color::Hsv(0, 160, 255)
    );

    match msg {
        Message::ChangeColor(Color::Rgb(r, g, b)) => {
            println!("Change color: red {}, green {}, and blue {}", r, g, b)
        }
        Message::ChangeColor(Color::Hsv(h, s, v)) => {
            println!("Change color: hue {}, saturation {}, and value {}", h, s, v)
        }
    }
    _ => (),
}
```

---

```rust
struct Point {
    x: i32,
    y: i32,
}

fn main() {
    // destruct 3 and 10 into `feet` and `inches` 
    let ((feet, inches), Point { x, y }) = ((3, 10), Point { x: 3, y: -10 });
}
```

## Ignoring Values in a Pattern
`_` can be used anywhere to signify ingoring of the value.

This could be useful when we need a function signature to be something specific but we're not gonna use all the arguments passed in. The `_` avoid compiler warning for unused parameters.

```rust
fn main() {
    foo(3, y);
}

fn foo(_, i32, y: i32) {
    println!("This code only uses the y parameter: {}", y);
}
```

### To ignore part of a value
If the setting has no value then we can set a value, however if the setting already has a value then we can't modify it.
```rust
fn main() {
    let mut setting_value = Some(5);
    let new_setting_value = Some(10);

    match (setting_value, new_setting_value) {
        // if both are `Some<T>` variant then 
        (Some(_), Some(_)) => {
            println!("Can't overwrite an existing customized value")
        }
        _ => {
            setting_value = new_setting_value
        }
    }
    
    println!("setting is {:?}", setting_value);
}
```

### To ignore values at multiple places withing one pattern

```rust
fn main() {
    let numbers = (2, 4, 8, 16, 32);

    match numbers {
        (first, _, third, _, fifth) => {
            println!("Some numbers: {}, {}, {}", first, third, fifth)
        }
    }
}
```

### Unused variables
The compiler won't complain.

```rust
fn main() {
    let _x = 5;
    let y = 10;
}
```

Prefixing a name with `_` is different than just using `_`.

<mark class="v">Prefixing a variable name with `_` still binds the value.</mark> 

`_s` is still binding with `s`.

```rust
fn main() {
    let s = Some(String::from("Hello!"));

    // to avoid compiler complain from not using `s` inside we prefix it with `_`
    // but this moves value to `_s`
    if let Some(_s) = s {
        println!("found a string")
    }

    println!("{:?}", s);
    //               ^ error: moved value
}
```

Instead if we would have done this, then it would successfully compile:

```rust
fn main() {
    let s = Some(String::from("Hello!"));

    if let Some(_) = s {
        println!("found a string")
    }

    println!("{:?}", s);
}
```

## Range syntax to ignore values

```rust
fn main() {
    struct Point {
        x: i32,
        y: i32,
    }

    let origin = Point { x: 0, y:0, z: 0 };

    match origin {
        // ignore all field except `x`
        Point { x, .. } => println!("x is {}", x),
    }
}
```

```rust
fn main() {
    let numbers = (2, 4, 8, 16, 32);

    match numbers {
        (first, ..., last) => {
            println!("Some numbers: {}, {}", first, last);
        }
    }
}
```

But they should be unambigous. Something like this won't work:

```rust
(..., second, ...) => { }
```

## Match Guards
<mark class="v">A match guard is an additional if condition specified after the pattern in a match arm that must also match along with the pattern.</mark>

Useful for expressing complex ideas that patterns themselves cannot express.

```rust
fn main() {
    let num = Some(4);

    match num {
        Some(x) if x < 5 => println!("less than five: {}", x),
        //      ^^^^^^^^ a match guard
        Some(x) => println!("{}", x),
        None => (),
    }
}
```

Match guards also solve issues with shadowing inside the match block.

Here in this example, we want to execute some code when `x` is equal to `y`.

We can't use `y` inside the pattern because it will shadow the outside `y`. But we could use `y` inside of our match guard.

```rust
fn main() {
    let x = Some(5);
    let y = 10;

    match num {
        // match on any `Some<T>`; bind it to `n` and compare it to `y`.
        Some(n) if n == y => println!("Matched: x = {}", n),
        _ => println!("Default case, x = {:?}", x),
    }
}
```
 
Multiple patterns with match guards:

```rust
fn main() {
    let x = 4;
    let y = false;

    match x {
        // `x` has to either 4 or 5 or 6 AND `y` has to be true
        4 | 5 | 6 if y => println!("yes"),
        _ => println!("no"),
    }
}
```

## Bindings
<mark class="v">`@` operator let's us create a variable that holds a value at the same time we're testing that value to see whether it matches a pattern.</mark>

```rust
fn main() {
    enum Message {
        Hello { id: i32 },
    }

    let msg = Message::Hello { id: 5 };

    match msg {
        Message::Hello {
            // match `id` between 3 and 7 and also store it in `id_variable`
            // can be same as field name; instead of `id_variable`
            id: id_variable @ 3..=7, 
        } => println!("Found and id in range: {}", id_variable),
        Message::Hello { id: 10..=12 } => { // otherwise simpy use range operator
            println!("Found an id in another range")
        }
        Message::Hello { id } => {          // to bind the variable
            println!("Found some other id: {}", id)
        }
    }
}

```