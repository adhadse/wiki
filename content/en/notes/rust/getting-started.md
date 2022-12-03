---
title: "Getting Started"
description: "Installing Rust tools"
lead: ""
date: 2022-09-20T07:54:56+01:00
lastmod: 2022-09-20T07:54:56+01:00
images: []
draft: false
type: docs
menu: 
  notes:
    parent: "rust"
weight: 1
toc: true
---

This tutorial series is minified version of **The Rust Book**:
{{< link title="The Rust Programming Language" link="https://doc.rust-lang.org/stable/book/title-page.html" >}}

and follow up of this tutorial series:

{{< youtube id="OX9HJsJUDxA" >}}

So, if you like watching video tutorial, do check out the above series by Bogdan Pshonyak and follow up with the notes here.

## Installing Rust on Linux or macOS

```bash
curl --proto '=https' --tlsv1.3 https://sh.rustup.rs -sSf | sh
```

Check Rust version with: `rustc --version`

Then go ahead and install official Plugin/extensions for Rust and Rust-analyzer for your faviourite IDE.

## Hello, World in Rust

```bash
mkdir ~/projects
cd ~/projects
mkdir hello_world
touch main.rs
code .
```

And then write in `main.rs`
```rust
fn main() {
    println!("Hello World");
}
```

Let's compile this and run this:
```bash
rustc main.rs
./main.rs
```

In real world projects we're going to work with multiple files with dependencies and therefore we need a build system and package manager: **Cargo**.

Check it's version as: `cargo --version`

Let's create a new package named `hello_cargo`:
{{< alert title="Note">}}
In Rust the package names are supposed to be in all smallcase.
{{< /alert >}}

```bash
cargo new hello_cargo
```
which build a directory structure something like this:
```bash
.
├── Cargo.toml
├── .gitignore
└── src
    └── main.rs
```

The `Cargo.toml` contains information about the package, and list dependencies along with their aliases.

```toml
[package]
name = "hello_cargo"
version = "0.1.0"
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[dependencies]
```

To build using *Cargo*, let's cd into our newly created directory: `cd hello_cargo` and then:
```bash
cargo build
cargo run
```
This creates new `cargo.lock` (don't temper with this) `target` dir which contains bunch of other stuff and main executable file.

Run `cargo --help` to see more bunch of options.

{{< alert title="Note">}}
You can use `cargo check` to check program for errors without actually building an executable file, much faster.
{{< /alert >}}

---

The default tools on the rustup toolchain are:

1. **Cargo**: package manager and crate host for Rust
2. **Rustup**: the rust toolchain installer/updater/release switcher
3. **Rustc**: the rust compiler

To update Rust, simply run:

```bash
rustup update
```

and to uninstall:
```bash
rustup self uninstall
```