---
title: "Generic Types in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:02+01:00
lastmod: 2022-09-20T07:58:02+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 10
toc: true
---

## Extracting Functions
Generic lifetimes anf traits are ways to reduce code duplication.

But, first let's talk about code duplication. We are trying to find the largest number, this works but to again find the largest number from a vector we might need to write the logic again.

```rust
fn main() {
    let number_list = vec![34, 50, 25, 100, 65];

    let mut largest = number_list[0];

    for number in number_list {
        if number > largest {
            largest = number;
        }
    }

    println!("The largest number is {}", largest);
}
```

The obvious step to extract the logic into function and call it twice:

```rust
fn main() {
    let number_list = vec![34, 50, 25, 100, 65];
    let largest = get_largest(number_list);
    println!("The largest number is {}", largest);

    let number_list = vec![102, 52, 6000, 89, 54, 2, 43, 8];
    let largest = get_largest(number_list);
    println!("The largest number is {}", largest);
}

fn get_largest(number_list: Vec<i32>) -> i32 {
    let mut largest = number_list[0];

    for number in number_list {
        if number > largest {
            largest = number;
        }
    }
    largest
}
```

This work but the logic of `get_largest()` is tied to a concrete type `i32`, but what if wanted to get largest character in a vector.

```rust
let char_list = vec!['y', 'm', 'c', 'k'];
// error
// mismatched types
// expected struct `Vec<i32>` found struct `Vec<char>`
let largest = get_largest(char_list);
```

One way might be duplicate the function with different definition, accepting `char` vector. 

```rust 
fn get_largest_char(char_list: Vec<char>) -> char {}
```

But we can do better. We'll modify our original function to take in both sets of arguments using generic:

- Generic types are specified inside angle bracked right after function name.
- We can also have multiple generic types:
    ```rust
    fn get_largest<T, U, V>(number_list: Vec<i32>) -> i32 {}
    ```

```rust
// We do want to specify that the generic type could be anything 
// that could be compared, which requires knowledge of Traits.
// but let's just quickly fix it up here
fn get_largest<T: PartialOrd + Copy>(number_list: Vec<T>) -> T {
    let mut largest = number_list[0];

    for number in number_list {
        if number > largest {
            largest = number;
        }
    }
    largest
}
```

## Generics in Struct Definitions
```rust
struct Point {
    x: i32,
    y: i32
}

fn main() {
    let p1 = Point { x:5, y: 10};

    // error: mismatched types
    // what if we wanted to created a `Point` with floating numbers
    let p2 = Point { x: 5.0, y: 10.0};
}
```

Using Generics:

```rust
struct Point<T> {
    x: T,
    y: T
}

fn main() {
    let p1 = Point { x:5, y: 10};
    let p2 = Point { x: 5.0, y: 10.0};
}
```

This will work with `p1` with integers and `p2` with floating numbers, but if we wanted to mix the two, we'd be required to add another generic type:

```rust
struct Point<T, U> {
    x: T,
    y: U
}

fn main() {
    let p1 = Point { x:5, y: 10};      // works
    let p2 = Point { x: 5.0, y: 10.0}; // works
    let p3 = Point { x: 5, y: 10.0};   // works
}
```

## Generics in Enum Definitions
```rust
fn main() {
    enum Option<T> {
        Some(T),
        None
    }

    enum Result<T, E> {
        Ok(T),
        Err(E)
    }
}
```

## Generics in Method Definitions
```rust
struct Point<T> {
    x: T,
    y: T
}

// the generic `T` here is not tied 
// to `T` specified up here for struct `Point`
// available to all `Point` instances
impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

// this impl block is only for f64
// only available to those `Point` instance where
// x and y are both f64
impl Point<f64> {
    fn y(&self) -> f64 {
        self.y
    }
}
fn main() {
    let p = Point { x: 5, y: 10 };
    p.x();  // available
    p.y();  // not available

    let p1 = Point { x: 5.0, y: 1.0};
    p.x();  // available
    p.y();  // available
}
```

---
Let's go complex, introduce two generic types, `T` and `U`.

```rust
struct Point<T, U> {
    x: T,
    y: U
}

impl<T, U> Point<T, U> {
    // notice, mixup has it's own generic types, `V` and `W` scoped to this function
    // Why? Because we want `other` to potentially have different types
    // then the `Point` we're calling the function on
    // And we return a `Point` of mixuped type `T` from `self` and `W` from passed in `other`.
    fn mixup<V, W>(self, other: Point<V, W>) -> Point<T, W> {
        Point {
            x: self.x,
            y: other.y
        }
    }
}

fn main() {
    let p1 = Point { x: 5, y: 10.4 };
    let p2 = Point { x: "Hello", y: 'c'};

    let p3 = p1.mixup(p2);
    println!("p3.x = {}, p3.y = {}", p3.x, p3.y);
}
```

Running this program outputs:

```text
p3.x = 5, p3.y = c
```

## Performance Impact
We don't need to define two versions of the `Option` enum using generic, and this also doesn't cost us in performance because at compile time, Rust will convert the `Option` enum into two option enums:

```rust
enum Option<T> {
    Some(T),
    None,
}

fn main() {
    let integer = Option::Some(5);
    let float = Option::Some(5.0);
}
```

```rust
enum Option_i32 {
    Some(i32),
    None,
}

enum Option_f64 {
    Some(f64),
    None,
}

fn main() {
    let integer = Option_i32::Some(5);
    let float = Option_f64::Some(5.0);
}
```