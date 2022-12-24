---
title: "Rust's Module System"
description: ""
lead: ""
date: 2022-09-20T07:57:59+01:00
lastmod: 2022-09-20T07:57:59+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 7
toc: true
---

We'll learn to manage growing projects using package, crates and modules. There is a requirement for organization and encapsulation of code as it grows in size.

Rust has a module system, starting with 
- **package**: `cargo new <name>` creates a new package, and package stores *crates*.
- **crates**: crates could either be binary crate, something which is executable or a library crate which is code that can be used by other programs. Crates contains *modules*.
- **modules**: modules allows us to organize a chunk of code and control the privacy rules.

If we wanted to create a module like Authentication, the internal function could remain private but expose one login method.

Rust also has **workspaces** meant for very large projects and allow us to store interrelated packages inside the workspace.

{{< link title="Managing Growing Projects with Packages, Crates, and Modules" link="https://doc.rust-lang.org/stable/book/ch07-00-managing-growing-projects-with-packages-crates-and-modules.html" >}}

## Packages and Crates
Let's start with creating a new package.

```bash
cargo new my-project
```

In the auto-generated `Cargo.toml` we can see that there are no crates defined, which doesn't mean our package dosn't have any crate.
```toml
[package]
name = "hello_cargo"
version = "0.1.0"
edition = "2021"
 
# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html
 
[dependencies]
```

Well, we actually do have **one binary crate**, for the `main.rs`. <mark class="y"> Rust follows the convention that if you have `main.rs` then a binary crate with the same name as your package will be automatically created and `main.rs` will be the crate root, which also makes the root module.</mark>

<mark class="y">The crate root is the source file that the rust compiler starts at when building your crate.</mark>

There is also a similar convention for library crate, for a file that might exist in `src` directory. Say, something like `lib.rs`.

```text
.
├── Cargo.toml
├── .gitignore
└── src
    ├── lib.rs
    └── main.rs
```
If `lib.rs` is defined in the root of our `src` directory, then rust will automatically create a library crate with the same name as your package, and `lib.rs` will be the crate root.

Which means our `my-project` has two crates, one binary and other a library crate.

{{< alert title="Crate Rules" >}}
1. A package must have at least one crate.
2. A package could have zero library crate or one library crate.
3. A package can have any number of binary crates.
{{< /alert >}}

So any other file like `another_file.rs` will represent another binary crate.

```text
.
├── Cargo.toml
├── .gitignore
├── bin
|   └── another_file.rs
└── src
    ├── lib.rs
    └── main.rs
```

## Defining Modules
Let's start by creating a new package `restaurant` that contain a library crate.

```bash
cargo new --lib restaurant
```

```text
.
├── Cargo.toml
└── src
    └── lib.rs
```

In which `lib.rs` we automatically get a test module something like this, which we don't need right now, so delete it.

```rust
pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

Our goal with new package is to create a library to help run a restaurant. Think about restaurant as two parts, *front of house* which serves customers, *back of house* where food is made.

```rust
// lib.rs
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}
        fn seat_at_table() {}
    }

    mod serving {
        fn take_order() {}
        fn serve_order() {}
        fn take_payment() {}
    }
}
```

We start with a module defined using `mod` keyword called `front_of_house`. Inside which we have two more module called `hosting` and `serving`.<mark class="g"> Modules can contain other modules, enums, structs, constants, traits and so on inside of them.</mark> 

So our module tree looks something like this:

```text
crate
 └── front_of_house
     ├── hosting
     │   ├── add_to_waitlist
     │   └── seat_at_table
     └── serving
         ├── take_order
         ├── serve_order
         └── take_payment
```

At top we have a module called <mark class="y">`crate` that gets created by default for our crate root which is `lib.rs`.</mark>

## Paths
A good analogy for module tree is to thinking about them like the folder/directory tree on computer.
If we wanted to reference a file inside a directory, in the same way we'd want to reference a item in a module, we'd be required to specify a path to that function.

Check the code below, a simplied `front_of_house` module inside of which we have `hosting` module which declares `add_to_waitlist()` function. 

We want to call this function in `eat_at_restaurant()`, we need to specify the path (specified using identifier separated by double colon) which could either be:

- Absolute path
- Relative path: start from current module


```rust
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {
    // Absolute path
    crate::front_of_house::hosting::add_to_waitlist();

    // Relative path
    front_of_house::hosting::add_to_waitlist();
}
```

## Module Privacy Rules
<mark class="r">Our code above will show error for `hosting` because `mod hosting` is private.</mark> 

{{< alert title="Hiding implementation details" type="success">}}
This is because in Rust by default a child and module and everything inside of it is private from the perspective of the parent module.

Child modules can see anything that's defined in their parent module.
{{< /alert >}}

If we want to expose any entity inside our module for public access, include `pub` keyword in front of it.

```rust
mod front_of_house {
    pub mod hosting {
        // this function will be private from `hosting`'s perspective
        pub fn add_to_waitlist() {}
    }
}
```

---
Let's look at another example with relative paths using `super` keyword.

```rust
// lib.rs
fn server_order() {}

mod back_of_house {
    fn fix_incorrect_order() {
        cook_order(); // can call because defined in same module
        super::serve_order(); // super to reference parent module, i.e., crate
    }

    fn cook_order() {}
}
```

---

Privacy rules with Structs.

In this example we have module called `back_of_house` storing a Struct `Breakfast` and an [`impl`](/notes/rust/structs-in-rust/#method-syntax) block implementing as associated function `summer()`.

```rust
mod back_of_house {
    struct Breakfast {
        toast: String,
        seasonal_fruit: String,
    }

    impl Breakfast {
        fn summer(toast: &str) -> Breakfast {
            Breakfast {
                toast: String::from(toast),
                seasonal_fruit: String::from("peaches"),
            }
        }
    }
}

pub fn eat_at_restaurant() {
    let mut meal = back_of_house::Breakfast::summer("wheat");
}
```

<mark class="r">But this fails, because `Breakfast` as well as `summer()` associated function are both private by default.</mark>

To fix, once again add `pub` keyword before each one.

```rust
mod back_of_house {
    pub struct Breakfast {
        toast: String,
        seasonal_fruit: String,
    }
 
    impl Breakfast {
        pub fn summer(toast: &str) -> Breakfast {
            Breakfast {
                toast: String::from(toast),
                seasonal_fruit: String::from("peaches"),
            }
        }
    }
}
 
pub fn eat_at_restaurant() {
    let mut meal = back_of_house::Breakfast::summer("wheat");
}
```

If we want to change the toast of `meal` of type `Breakfast` we'll get an error, because field itself are also private by default.

```rust
pub fn eat_at_restaurant() {
    let mut meal = back_of_house::Breakfast::summer("wheat");
    meal.toast = String::from("Rye"); // error!
}
```

Again add `pub` keyword infront of `toast` field.

```rust
pub struct Breakfast {
    pub toast: String,
    ...
```

We can't build `Breakfast` struct directly because it contains a private field, which is inaccessible.

The same privacy rules also applies to Enums.

## The Use Keyword

Here specifying the full path of a function (as in below example calling `add_to_waitlist()` called 3 three times) isn't pretty or ideal.

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {
    front_of_house::hosting::add_to_waitlist();
    front_of_house::hosting::add_to_waitlist();
    front_of_house::hosting::add_to_watilist();
}
```

To deal with this problem, Rust provides us the `use` keyword.

<mark class="y">`use` keyword allow us to bring a path into a scope.</mark>

Let's bring `hosting module into the scope:

```rust
use crate::front_of_house::hosting;

// or use relative path; use only `self` to reference current module.
use self::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
}
```

{{< alert title="Idiomatic use of paths">}}
1. It's idiomatic to bring the function's parent module into scope, since that would allow us to minimize the path we've to specify but we're also making it the function used isn't local.
2. If we're bringing Enums, Structs or other items into scope, it's idiomatic to specify the full path when using `use` keyword.

    An exception is that if you are bringing two items from different modules having same name, then bring parent module into scope so that names don't conflict.
{{< /alert >}}

As an example in the below example both function return a [`Result`](https://doc.rust-lang.org/std/result/) type defined in two different modules, without conflicting:

```rust
use std::fmt;
use std::io; 

fn function1() -> fmt::Result {}
fn function2() -> io::Result<()> {}
```

Another way could be to rename one of the Result type when bringing it into scope.

```rust
use std::fmt::Result;
use std::io::Result as IoResult;

fn function1() -> Result {}
fn function2() -> IoResult<()> {}
```

---
Back to Restaurant example, let's talk about re-exporting.

What if we wanted to make the function `add_to_waitlist()` available to any external code.

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}
use crate::front_of_house::hosting;
 
// currently only `eat_at_restaurant()` is available outside of this file because of `pub` keyword
pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
    hosting::add_to_waitlist();
}
```

To re-export the `hosting` module, add `pub` keyword infront of `use` statement. This allows external code to reference the `hosting` module as well as use it at the same time.

```rust
pub use crate::front_of_house::hosting;
```

---
`use` keyword also allows us to bring in items from external dependencies as defined in `Cargo.toml` into a scope.

For example, let's add a `rand` dependencies to `Cargo.toml`.

```toml
# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html
 
[dependencies]
rand = "0.5.5"
```

Then we can bring `Rng` trait into scope using `use` keyword in `lib.rs`

```rust
use rand::Rng;

mod front_of_house {
    // ...
}

pub fn eat_at_restaurant() {
    let secret_number = rand::thread_rng().gen_range(1..101);
    ...
}
```

And we can bring multiple items using Nested paths:
```rust
use rand::{Rng, CryptoRng, ErrorKind::Transient};
```

Instead of bringing `io` and `Write` into scope both in `io` module like this:
```rust
use std::io;
use std::io::Write;
```

we can write it as:
```rust
use std::io::{self, Write};
```

## The Glob Operator
<mark class="y">Bring all the public items underneath a module into scope.</mark>

Bringing all public items from `io` into scope.
```rust
use std::io::*;
```

## Modules in Separate Files
As programs grow module get's large in size, in that we would want to move module definition into another file.

Let's move `front_of_house` to new file:

```rust
// src/front_of_house.rs
pub mod hosting {
    pub fn add_to_waitlist() {}
}
```

and in `lib.rs` we'll write something like below which tells Rust to <mark class="g"> define module `front_of_house` here but get contents from a different file/folder named same as `front_of_house`</mark>:

```rust
// src/lib.rs
// or src/main.rs
mod front_of_house;
```

--- 
Let's extract the definition of `hosting` module into separate file, making the whole module a directory, which can consist of different files.

```rust
// src/front_of_house/hosting.rs
pub fn add_to_waitlist() {}
```

You can either delete `src/front_of_house.rs` and add `src/front_of_house/mod.rs` with following content.

```rust
// src/front_of_house/mod.rs
pub mod hosting;
```

Or keep `src/front_of_house.rs` and change it's content to:

```rust
// src/front_of_house.rs
pub mod hosting;
```