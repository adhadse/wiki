---
title: "Macros in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:31+01:00
lastmod: 2022-09-20T07:58:31+01:00
images: []
type: docs
draft: false
menu: 
  rust:
    parent: "advanced"
weight: 5
toc: true
---

{{< link title="Macros" link="https://doc.rust-lang.org/stable/book/ch19-06-macros.html" >}}

## Macros and Functions Difference
<mark class="v">Macros allows us to write code *which writes other code* known as **Meta Programming**</mark>

Think of macros kind of like a function where the input is code and output is also code that is transformed in some way.

We've seen macros until now a lot of time:

- `println!` 
- `vec!`

By using macros we can reduce the amount of code we have to write and maintain which is similar to functions, but there are few differences:

- Functions must declare the number of parameters they could accept whereas macros can accept a variable number of parameters. 
- Functions are called at runtime whereas macros are expanded before our program finishes compiling.

So yes, macros are powerful but it also introduces complexity, since your code writes other code, meaning macros being harder to read, understand and maintain.

Rust has two forms of macros:
1. **Declarative macros**
2. **Procedural macros**

# Declarative Macros
## Declarative Macros
Declarative macros are most common macros used across Rust code, allows us to write something similar to a match expression.

For this example, we'll create a new project exactly like library crate we're using before with `lib.rs` as well:

```text
.
├── Cargo.toml
├── .gitignore
└── src
    ├── lib.rs
    └── main.rs
```
We can pass different type to `vec!` macro generating different `Vec<T>` types and pass in variable amount of arguments.

```rust
// main.rs
fn main() {
    let v1: Vec<u32> = vec![1, 2, 3];
    let v2: Vec<&str> = vec!["a", "b", "c", "d", "e"];
}
``` 

In `lib.rs` we've implemented how `vec!` macro is implemented (a simplified version of `vec!` macro from std library):

```rust
// lib.rs
#[macro_export]
macro_rules! vec {
    ( $( $x:expr ),* ) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}
```

Let's go through it:

- `#[macro_export]` means that whenever the crate in which this macro is defined is brought into scope this macro should be made available.
- start defining the macro with `macro_rules!` followed by name of our macro `vec` which then follows `{}` containing the body
- The body is similar to match expression with one arm (but can have many), 

    - `( $( $x:expr ),* )` is a pattern to match followed by a code block.
    - If inputs to our macro match this pattern then the code runs otherwise error is generated since we have only one arm.
- The pattern syntax used in macros is different than the pattern syntax in match expression because we're matching against actual code versus value.

```rust
  ( $( $x:expr ),* )
//  ^^^^^^^^^^^^|└── * to indicate our pattern can match zero or more times  
//  |           └── suggest comma could appear after the code which matches the pattern
//  | implies: capture any value that match the pattern inside the (), 
//  | for use in replacement code
```

`$x:expr` matches any Rust expression and assigns it to variable `$x`.

When calling our macro with input: `vec![1, 2, 3]` our pattern here is going to match three times once for every expression in the code we pass in.

- First, the `expr` will match with `1` assign it to `x`, then with `2` assign it to `x` and lastly match it with `3` and assign it to `x`.
- The body stores the code that's going to be generated. First we create a mutable vector `temp_vec`.
- Then we have this, which says generate this line of code for every match that we get,

    ```rust
    $(
        temp_vec.push($x);
    )*
    ```
    with `$x` replaced with whatever we match on. So the output will look something like this:

    ```rust
    {
        let mut temp_vec = Vec::new();
        temp_vec.push(1);
        temp_vec.push(2);
        temp_vec.puhs(3);
        temp_vec
    }
    ``` 

Obviously this is a very simple example of macros.

This book should give you a deeper dive into writing macros in Rust:

{{< link title="The Little Book of Rust Macros" link="https://veykril.github.io/tlborm/" icon=":book:" >}}

# Procedural Macros
## Procedural Macros
Procedural Macros are like functions. They take code as input, operate on that code and produce code as output.

In contrast, declarative macros match against which match against patterns and repace code with other code.

Their are three kinds of procedural macros:
1. Custom Derived
2. Attribute like
3. Function like

Procedural macros must be defined in their own crate with a custom crate type. All the three kinds of procedural macros are all defined using a similar syntax:

```rust
use proc_macro;

#[some_attribute]
pub fn some_name(input: TokenStream) -> TokenStream {
    // ...
}
```

The name of the function `some_name` is the name of our procedural macro and input is going to be `TokenStream`, the code on which we're operating on and the output is also going to be a `TokenStream`, the code macro is going to produce.
- Tokens are smallest individual elements of a program, reperesenting keyword, identifiers, operators etc. Our function must also have an attribute which specifies what kind of procedural macro we're creating.

So how can we make our own custom derived macro, `hello_macro` implementing a trait also named `hello_macro` which will have an associated function with a default implementation that prints "hello macro".


This is how we'll use it:

```rust
// lib.rs

// bringing our macro into scope
// why we need two? we'll talk about that later
use hello_macro::HelloMacro;        
use hello_macro_derive::HelloMacro;

// derive attribute specifying our macro
#[derive(HelloMacro)]
struct Pancakes;

fn main() {
    Pancakes::hello_macro();
}
```

The derive attribute will implement our `hello_macro` trait for the `Pancakes` struct, allowing `hello_macro()` from `Pancake` struct.

To implement our proc/procedural macro we'll create a new project **in new directory**: 

```bash
cargo new hello_macro --lib
cd hello_macro               # change directory 
code .                       # open your editor 
```

and edit the `lib.rs` in this directory:

```rust
// lib.rs
pub trait HelloMacro {
    fn hello_macro();
}
```

Our new macro has one associated function `hello_macro()`. Now we did wanted to have a default implementation but we have a problem. We could simply write a default implementation if all it would do was to print something. 

**But** imagine we wanted to do a little bit comlicated by printing "hello macro" followed by the type on which the trait was implemented (for example here it's `Pancakes`) on.

Rust doesn't have *Reflective capabilities* so we can't look up the name of the type (`Pancakes`) at runtime.

<mark class="y">The solution is to use our macro to generate default implementation.</mark>

We talked earlier that the procedural macros have to be defined in their own crate. So we're going to create a new library crate **inside** of our `hello_macro` crate:

```bash
cargo new hello_macro_derive --lib
```

This should create something like this:

```text
hello_macro
├── hello_macro_derive   
│   ├── src
│   │   └── lib.rs
│   ├── .gitignore
│   ├── target/
│   ├── Cargo.lock
│   └── Cargo.toml
├── src
│   └── lib.rs
├── .gitignore
├── target/
├── Cargo.lock
└── Cargo.toml
```

<mark class="g">The naming convention when structuring crates and macros crates states, if we have a custom derived macro then we'll name the crate whatever our crate name was (in our case `hello_macro`) and append `_derive` (resulting in `hello_macro_derive`).</mark>

Because these two crates are tightly coupled we created our macro crate inside of our library crate, although each crate has to be published separately and code using them has to bring each crate into scope. 

Let's check `Cargo.toml` file in our newly created `hello_macro_derive` crate and edit it to <mark class="y">signify it's a special trait for macro</mark>

```toml
[package]
name = "hello_macro_derive"
version = "0.1.0"
edition = "2021"
 
# enable this
[lib]
proc-macro = true

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

# add these dependencies 
[dependencies]
syn = "1.0"
quote = "1.0"
```

Now let's open `hello_macro_derive/src/lib.rs` file and replace the code:

```rust
extern crate proc_macro;

use proc_macro::TokenStream;
use quoate::quote;
use syn;

#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    // Construct a Abstract Syntax Tree of Rust code from TokenStream
    // that we can manipulate
    let ast = syn::parse(input).unwrap();

    // Build the trait implementation
    impl_hello_macro(&ast)
}
```

- `proc_macro` is a crate that comes with Rust, so don't have to declare it in `Cargo.toml` file but we do need to import it so we have `extern crate` statement.
    - <mark class="v">`proc_macro` crate allows us to read and manipulate Rust code</mark> 
- `syn` crate (short for *syntax*) allows us to take a string of Rust code into a syntax tree data structure.
- `quote` crate can take this syntax tree data structure and turn it back into Rust code.
- Then we have defined our custom derived macro broken into two parts:
    - first will be reponsible for parsing `TokenStream` input into a syntax tree and is going to be the same for almost all procedural macros 
    - `impl_hello_macro()` function is reponsible for transforming that syntax tree
The part which actually manipulates the syntax tree is going to be different.
- The function is annotated with `proc_macro_derive` indicating this is a custom derived macro with the name `HelloMacro`

Let's see the `impl_hello_macro()` function written in continuation of the previous function:

```rust
fn impl_hello_macro(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;   // the name of the type we're working on
    let gen = quote! {       // use quote macro to output some Rust code
        impl HelloMacro for #name {
            fn hello_macro() {
                println!(
                    "Hello, Macro! My name is {}!",
                    stringify!(#name)
                );
            }
        }
    };
    gen.into()
}
```

Inside the `quote!` macro we just want to implement `HelloMacro` for our type indicated by template variable `#name` made available by `quote!` macro. This will be replaced by `quote!` macro. Then we provide a custom implementation for `hello_macro()` associated function. The `stringify!` macro will take an expression and turn it into a string without evaluating the expression (like the `format!` macro would do). At last we just get the outuput saved in `gen` and turn in `TokenStream` by calling `into()` method on it.

Running `cargo build` to build `hello_macro_derive` crate.

Then cd out and build `hello_macro` crate:

```bash
cd ..
cargo build
```

Now we can switch back to our main project where we were testing our macros and add our macro crates as dependencies:

Since we didn't published them, we just provide path to them.

```toml
[package]
name = "advanced"
version = "0.1.0"
edition = "2021"
 
# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

# add these dependencies 
[dependencies]
hello_macro = { path = "../hello_macro" }
hello_macro_derive = { path = "../hello_macro/hello_macro_derive" }
```

And this should compile fine with `cargo run`.

## Attribute-like macros
These are similar to custom derived macros except instead of generating code for the derive attribute we can create a custom attribute.

Also custom derived macros only work on structs & enums whereas attribute-like macros work on other types such as functions.

For example we're building a web framework and we want to create a new attribute called `route` which takes in https method and the route. 
```rust

// This macro will generate code which will map a specific 
// http request to a given function 
// a get request to the `index()` function
#[route(GET, "/")]
fn index() {
    // ...
}

// annotation to define an attribute-like macro like this with 
#[proc_macro_attribute]
pub fn route(
    attr: TokenStream, // contents of the attribute | GET, "/"
    item: TokenStream, // contents of the item the attribute is attached to | fn index() {}
) -> TokenStream {
    // ...
}
```

## Function-like macros
They look like function calls however they are more flexible. <mark class="v"> Firstly they could take a variable number of arguments and secondly they operate on Rust code.</mark>

In this example we want to generate a function like macro sql which will SQL statement as as argument, validate it's syntax and generate code to allow us to execute that statement.

```rust
let sql = sql!(SELECT * FROM posts WHERE id=1);

// the only difference being we annotate the function with `proc_macro`
// instead of `proc_macro_derive`
#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
    // ...
}
```