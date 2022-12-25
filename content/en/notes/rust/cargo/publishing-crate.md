---
title: "Publishing a Rust Crate"
description: ""
lead: ""
date: 2022-09-20T07:58:11+01:00
lastmod: 2022-09-20T07:58:11+01:00
images: []
type: docs
draft: false
menu: 
  rust:
    parent: "cargo"
weight: 1
toc: true
---

{{< link title="More About Cargo and Crates.io" link="https://doc.rust-lang.org/stable/book/ch14-00-more-about-cargo.html" >}}

## Release Profiles
Release profiles allow us to configure how the code is compiled.

Cargo has two main profiles:
- `dev`: provide good defaults out of the box for development

    `cargo build` compiles and build with `dev` profile. `dev` build is also unoptimized and contains debug information
- `release`: good defaults for release build

    To build with release profile: `cargo build --release`

We can customize these settings in `Cargo.toml` file:

```toml
[package]
name = "..."
...

[dependencies]

[profile.dev]
opt-level = 0

[profile.release]
opt-level = 3
```

Here we added two sections for dev and release profile specifying `opt-level` settings which stands for optimization level, ranging from 0 to 3, 0 being no optimization and 3 for highest level of optimization.

So during development stages, we want the compilation to be as fast as possible trading off runtime performance with no-optimization and vice-versa during release.

For full list of all settings for profile section, refer documentation:

{{< link link="https://doc.rust-lang.org/cargo/reference/profiles.html" title="Profiles" >}}

## Documentation Comments
Documentation comments are useful when documenting your API for documentation purposes.

Documentation comments starts with three slashes, supports markdown and Rust can convert these comments into deployable Rust HTML documentation.

```rust
/// Adds one to the number given
///
/// # Examples
///
/// ```
/// let arg = 5;
/// let answer = my_crate::add_one(arg);
///
/// assert_eq!(6, answer);
/// ```
pub fn add_one(x: i32) -> i32 {
    x + 1
}
``` 

To build our doc (for testing purpose `open` in a web browser), open up a terminal and fire this command:

```bash
cargo doc --open
```

### Commonly used sections in documentation
Here are some other sections (created using `#` as in `/// # Examples` ) that crate developers commonly use:

- **Panics**: scenario in which functions would panic, so caller of the function don't use the function in those scenarios
- **Errors**: what kind of `Err` are generated when the function returns a `Result` and in which conditions. So callers can handle the error.
- **Safety**: If the function is `unsafe` to call, this section should describe why the function is unsafe and covering the invariants that the function expects callers to uphold.

### Documentation Comments as Tests
The documentation tests are signified by the `assert_eq!` macro and runs when you run `cargo test` to test the code credibility. This keeps the documentation and code in sync. 

### Commenting Contained Items
This style of comments documents the item containing the comment:

```rust
//! # My Crate
//!
//! `my_create` is a collection of utilities to make performing certain 
//! calculations more convenient
```
## Exporting a Public API
Let's create a new crate called `adhadse_art` which has a library crate: `lib.rs` consisting of two modules: `kinds` & `utils`:

In `lib.rs`:

```rust
//! # Adhadse Art
//!
//! A library for modeling artistic concepts.

pub mod kinds {
    /// The primary colors according to the RYB color model.
    pub enum PrimaryColor {
        Red, 
        Yellow,
        Blue,
    }

    /// The secondary colors according to the RYB color model
    pub enum SecondaryColor {
        Orange,
        Green,
        Purple,
    }
}

pub mod utils {
    use crate::kinds::*;

    /// Combines two primary colors in equal amounts to create 
    /// a secondary color.
    pub fn mix(c1: PrimaryColor, c2: PrimaryColor) -> SecondaryColor {
        // --snip--
        // ANCHOR_END: here
        SecondaryColor::Orange
        // ANCHOR: here
    }
}
```

To access the two enums, we might do something like this:

```rust
use adhadse_art::kinds::PrimaryColor;
use adhadse_art::utils::mix;

fn main() {
    let red = PrimaryColor::Red;
    let yellow = PrimaryColor::Yellow;
    mix(red, yellow);
}
```

This structure might make sense to us, the developer internally. 

**But what if we wanted to give access to these function & enums to users at the top level without referencing the respective modules?**

To do this go to `lib.rs` and reexport the enums and the `mix()` function:

```rust
//! calculations more convenient

pub use self::kinds::PrimaryColor;
pub use self::kinds::SecondaryColor;
pub use self::utils::mix;

pub mod kinds { 
    // ...
    // ...
```

then we can use these items from top level directly in `main.rs`:

```rust
use adhadse_art::PrimaryColor;
use adhadse_art::mix;

fn main() {
    // ...
}
```

## Setting up Crates.io account
1. Login into crates.io with your GitHub account
2. Go to "Account Settings" and click create "New Token" for API Access after givng the token a name.
3. This will create a new token, which should be kept private.
4. Copy the command and run it from the project's dir to save it to `~/.cargo/credentials` and login.
5. We can now publish our crate but not before checking the metadata.

## Adding Metadata to a New Crate
The metadata for crate is stored in `Cargo.toml` file at the top, something like this at top level:
- Keep in mind that the crate name should be unique, should not conflict with any other crate already published on crates.io.

```toml
[package]
name = "adhadse_art"
version = "0.1.0"
authors = ["Anurag Dhadse"]
edition = "2021"
```

Before we can publish, we'll need to add `description` and `license` fields, so let's quickly add that following other fields:

```toml
description = "A library for modeling artistic concepts"
license = "MIT"
```

and then publish it:

```bash
cargo publish
```

## Removing Version from Crates.io
Although you can't delete the crate once its published, to avoid breaking dependencies other project might be using. But we can stop versions from being downloaded, in case of a security flaw or discontinuation.

To do this use `cargo yank` command passing it the version to yank:

```bash
cargo yank --vers 0.1.0
```

<mark class="v">Now, those who is using this specific version right now, will be allowed to download the library, BUT for anyone who want to use it for the first time won't be allowed to download.</mark>

To undo this, simply pass in `--undo`:

```bash
cargo yank --vers 0.1.0 --undo
```