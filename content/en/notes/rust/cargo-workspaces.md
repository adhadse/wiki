---
title: "Cargo Workspaces"
description: ""
lead: ""
date: 2022-09-20T07:58:12+01:00
lastmod: 2022-09-20T07:58:12+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 16
toc: true
---

What happens when the program keep growing and have multiple library crates? That's where cargo workspace comes for the rescue.

- Workspaces help you manage multiple related packages that are being developed
- Packages in a workspace share common dependency resolution, since they have only one `Cargo.lock` file.
- Packages in a workspace also share one output directory and release profiles.

## Creating a Workspace
We are going to create one binary that depends on one library.
- First library having `add_one` function.

Begin by creating a directory and opening it in an editor:

```bash
mkdir add
cd add
code .
```

Next we'll add a `Cargo.toml` file to configure our workspace, by creating a `worspace` section instead of a `package` section.
- Then we'll specify the members of the workspace called **workspace members** specifying the path to the packages.

```toml
[workspace]

members = [
  "adder"
]
```

Then we'll add a new package `adder` and even try building it:

```bash
cargo new adder
cargo build
```

The newly created package will *not* have a target folder or `Cargo.lock` file but instead at root of our workspace, signifying the packages in a workspace are meant to depend on each other. <mark class="y">Meaning if each package had its own target directory, when you would compile that package, you would have to also compile all its dependencies.</mark><mark class="g"> But now they are combinely managed in a single workspace with **same dependencies**, reducing the amount of compilation required.</mark>

## Creating Second pacakge in Workspace
Update the root `Cargo.toml` file:

```toml
[workspace]

members = [
  "adder",
  "add-one",
]
```

We'll add a second package `add-one` and specifying `--lib` for library:

```bash
cargo new add-one --lib
```

Update the `add-one/src/lib.rs` file:

```rust
pub fn add_one(x: i32) -> i32 {
    x +1
}
```

Next, we need to specify that our `adder` binary depends on `add-one` library. We'll do this by updating `adder`'s `Cargo.toml` file:
- Cargo by default don't assume that crates within a workspace depend on each other.

```toml
[dependencies]
add-one = { path = "../add-one" }
```

Now we can use our newly created library in `adder` binary, in `adder/src/main.rs`:

```rust
use add_one;

fn mian() {
  let num = 10;
  println!(
      "Hello, world! {} plus one is {}!",
      num,
      add_one::add_one(num)
  );
}
```

To build our workspace run the build command from the root of workspace:

```bash
cargo build
```

Next we can the adder binary from the root of our workspace by running:

```bash
cargo run --package adder
```

## External dependencies
Since all the packages uses one single `Cargo.lock` for dependency resolution, this ensures that the packages are compatible with each other.
- If we add a dependency to `add-one` package and `adder` package, they both will resolve to the same version.

If we add a `rand` dependency to `Cargo.toml` file of `add-one` package and use it somewhere in `lib.rs`:

```toml
[dependencies]
rand = "0.8.3"
```

```rust
use rand;

pub fn add_one(x: i32 ) -> i32 {
  // ...
```



Then from the root of the package we can build the workspace: `cargo build` which adds `rand` as a dependency for the `add-one` package.

We can't use the `rand` dependency however in `adder` package until we add it as a dependency for `adder` in it's `Cargo.toml` file:

```toml
[dependencies]
add-one = { path = "../add-one" }
rand = "0.8.3"
```

## Adding a Test to a Workspace
Let's add one test module inside `lib.rs` file of `add-one` package:

```rust
pub fn add_one(x: i32) -> i32 {
  //...
  // ..

#[cfg(test)]
mod tests {
  use super::*;

  #[test]
  fn it_works() {
    assert_eq!(3, add_one(2));
  }
}
```

Now run `cargo test` from workspace root. This will run all package-tests and documentation tests.

If we wanted to run tests for a specific package we could run it using `-p` or `--package` option specfying the specific package:

```bash
cargo test -p add-one
```

To publish a package from a workspace we have to do it individually for each package.

## Installing Binaries from Crates.io
Although this isn't meant as a replacement for package managers like `dnf` or `apt` but as a convenient tool to install tools published on crates.io <mark class="y">having a binary target</mark>.
- All binaries are stored in Rust installation routes bin directory.

If installed via `rustup` this would be the path to that bin directory (can be requirement to add it to PATH, so that other programs use the Rust installed binaries):

```bash
~/.cargo/bin
```

Let try this out by installing `riprep`, the implementation of `grep` in Rust.

```bash
cargo install ripgrep
```

{{< alert title="Extending Cargo">}}
If you have a binary named starting with `cargo-`, say `cargo-something`, then this can be used by `cargo` as a command (sub command) to extend its functionality:

```bash
cargo something
```
{{< /alert >}}

