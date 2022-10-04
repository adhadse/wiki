---
title: "Enums and Pattern Matching in Rust"
description: ""
lead: ""
date: 2022-09-20T07:57:58+01:00
lastmod: 2022-09-20T07:57:58+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 6
toc: true
---

## Defining Enums
Enums allow us to enumerate a list of variants.

When is it appropriate to use Enums over Structs? Take an example of IP Addresses, whose all variants can be enumerated, which are just two v4 and v6. And we can express these variants in our code for IP addresses.

```rust
enum IPAddrKind {
    V4,
    V6,
}

fn main() {
    let four = IPAddrKind::V4;
    let six = IPAddrKInd::V6;
}

// a function that accepts variables of type `IPAddrKind`
fn route(ip_kind: IPAddrKind) {}
```

## Enums in Structs
The Enums defined above are able to capture the version of IP address, but what if we wanter to capture the actual IP address as well?

```rust
enum IPAddrKind {
   V4,
   V6
}

// group version of IP address with actual IP address
struct IPAddr {
    kind: IPAddrKind,
    address: String
}

fn main() {
    let four = IPAddrKind::V4;
    let six = IPAddrKInd::V6;

    let localhost = IPAddr {
        kind: IPAddrKind::V4,
        address: String::from("127.0.0.1")
    }
}
```

## Values inside Enums
What if we can store the data directly inside the Enum variants? This is done by adding Paranthesis `()` and specifying what type of data does the variant stores.

```rust
enum IPAddrKind {
   V4(String),
   V6(String)
}

fn main() {
    let localhost = IPAddrKind::V4(String::from("127.0.0.1"));
}
```

Enum variants can store wide variety of types. To demostrate let's write a `Message` Enum.

```rust
enum Message {
    Quit,                      // stores no data
    Move {x: i32, y: i32},     // stores anonymous struct
    Write(String),             // stores a String 
    ChangeColor(i32, i32, i32) // stores three integers
}
```

## Enum Methods
Just like Struct, Enum methods and associated functions can be written using `impl` block.

```rust
impl Message {
    fn some_function() {
        println!("Hello, World!");
    }
}
```

## The Option Enum
Many languages out there, suffers from the sin of `Null` values, which are useful to represent whether a value exist or is it null, i.e., there is no value. The problem is the type system can't guarantee if you use a value it's not null. 

Which leads to Runtime Exception, like `NullPointerException` or languages like Kotlin trying to solve the issue by introduing operator `?` to check if it's null or not.

In Rust there are no NULL values. Instead we have `Option` enum, which looks something like this (You don't define it, Rust has already defined it for you) and are included in our program scope by default:

```rust
enum Option<T> {
    Some(T),   // stores some value of generic type T
    None       // No value
}
```

{{< alert type="success" >}}
So if you have any value that could potentially be null/not exist, then you would wrap it in `Option` Enum.
{{< /alert >}}

{{< alert title="When to use Option or Result type?" type="success">}}
- **Options (to be, or not to be)**

    Briefly stated, an Option type can either be something or nothing. For example, the value `Some(10)` is definitely something: an integer wrapped in `Some`, whereas None is a whole lot of nothing.

    ```rust
    enum Option<T> {
        Some(T),   
        None  
    }
    ```

- **Results (is everything ok?)**

    This may hold something, or an `error`. Whereas the `Option` type uses either `Some` to wrap successful results or `None`, the Result type uses `Ok` to wrap successful results or `Err` to wrap error information for the situations when things have gone south, e.g. `Ok(3.14159)`, and `Err("This Bad Thing Happened")`.

    ```rust
    enum Result<T, E> {
        Ok(T),
        Err(E),
    }
    ```

{{< /alert >}}
This allows type system to enforce that we handle the `none` case when value doesn't exist and in `some` case the value is present

```rust
fn main() {
    let some_number: Option<i32> = Some(5);
    let some_string: Option<&str> = Some("a string");

    // You don't need to annotate the above variables.
    // except in below case where no value is passed in so we were
    // required to annotate
    let absent_number: Option<i32> = None;
}
```

{{< alert type="danger" >}}
You can't do something like this: 

```rust
fn main() {
    let msg = None;
}
```

The compiler will complain:

```text
error[E0282]: type annotations needed for `Option<T>`
 --> src/main.rs:4:9
  |
4 |     let msg = None;
  |         ^^^
  |
help: consider giving `msg` an explicit type, where the type for type parameter `T` is specified
  |
4 |     let msg: Option<T> = None;
  |            +++++++++++

For more information about this error, try `rustc --explain E0282`.
error: could not compile `playground` due to previous error
```
{{< /alert >}}

--- 

Let's look at another example, where we try to add an integer and an optional integer:

```rust
fn main() {
    let x: i8 = 5;
    let y: Option<i8> = Some(5);

    // well, you can't 
    // error[E0277]: cannot add `Option<i8>` to `i8`
    let sum = x + y;
}
```

For this code to work, we need to extract our integer out of the `Some` varient. In general to extract values out of `Some` varient, we'll be required to handle all possible varients, like if the variant is `Some` we are allowed to safely use the value, otherwise branch out.

<mark class="y">`Option` Enum has some very useful set of method, for example, here we can use `unwrap_or()` method on `y` to use value if it exist, otherwise use the default value.</mark>

```rust
fn main() {
    ...
    let sum = x + y.unwrap_or(0);
}
```

## Using Match Expressions
We already know that match allows us to compare a value against the set of patterns. 

This makes a `match` expression very useful for Enums, to match a variable of an Enum variant. `match` expressions are exhaustive meaning that we have to match all possible value.

```rust
enum Coin {
    Penny,
    Nickel,
    Dime, 
    Quarter,
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25
    }
}
```

These patterns can also bind to values.

```rust
// enum to represent the state minted on each quarter
#[derive(Debug)]
enum UsState {
    Albama,
    Alaska,
    Arizona,
    Arkansas,
    California,
    //...
}

enum Coin {
    Penny,
    Nickel,
    Dime, 
    Quarter(UsState),
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(state) => {
            println!("State quarter from {:?}!", state);
            25
        }
    }
}
```

Let write our main function and call this function:

```rust
fn main() {
    value_in_cents(Coin::Quarter(UsState::Alaska));
}
```

Which prints:

```text
State quarter from Alaska!
```

---
Let's try to combine the `match` expression with `Option` enum.

```rust
fn main() {
    let five = Some(5);
    let six = plus_one(five);
    let none = plus_one(None);
}
fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i+1),
    }
}
```

Since `match` expressions are exhaustive, we need to match for all possible variants. If we can't write the match arm for all possible variants, then we can use `_` to match for everything else.

```rust
match coin {
    Coin::Penny => 1,
    Coin::Nickel => 5,
    _ => {
        println!("Some value.");
        0
    }
}
```

## Using if let Syntax
```rust
fn main() {
    let some_value = Some(3);
    // we only care about one variant, otherwise do nothing
    match some_value {
        Some(3) => println!("three"),
        _ => (),
    }
}
```

This is a little verbose, we can make it more concise using `if-let` sytanx.<mark class="y"> With `if-let` sytanx we only specify the pattern we care about.</mark>
```rust
fn main() {
    let some_value = Some(3);

    // start with `if-let` and rest is read backwards, i.e.,
    // if `some_value` matches `Some(3)` then print "three"
    if let Some(3) = some_value {
        println!("three");
    }
}
```