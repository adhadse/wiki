---
title: "Testing in Rust - Part 2"
description: ""
lead: ""
date: 2022-09-20T07:58:06+01:00
lastmod: 2022-09-20T07:58:06+01:00
images: []
type: docs
draft: false
menu: 
  rust:
    parent: "testing"
weight: 2
toc: true
---

{{< link title="Test Organization" link="https://doc.rust-lang.org/stable/book/ch11-03-test-organization.html" >}}

We'll learn how to run tests in different ways and how to organize them into integration tests and unit tests.

## Controlling How Tests Run
We'll continue with the `adder` crate we built earlier with `it_works()` test plus one more added `it_works2()` test function:

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn it_works() -> Result<(), String> {
        if 2 + 2 == 4 {
            Ok(())  // Success case is unit type
        } else {
            Err(String::from("two plus two does not equal four"))
        }
    }

    #[test]
    fn it_works2() {
      assert_eq!(2 + 2, 4);
    }
}
```

This test passes successfully. Cargo compiles your code in test mode and runs the resulting test binary.

We can change the default using command line arguments. By default all tests get run in parallel in a separate thread & all generated ouptut is captures and not printed to the screen.

There are two sets of command line options separated by `--`,
- one set is for `cargo test` command
- other set is for the resulting test binary.

So this print help page for `cargo test`, 

```bash
cargo test --help
```

If we want to figure out which commands we could pass to the resulting test binary:

```bash
cargo test -- --help
```

Here we have an option, `--test-threads` which can set the number of threads used for running tests in parallel:

```bash
cargo test -- --test-threads=1
```
Generally you don't want to do this because then you're test will run slower but in some cases this might be useful. For example in case we might have some tests that modify a file. Running a test parallely will corrupt the file or cause race condition. In that case it is suitable to use single thread for running test.

## Showing Output
 
```rust
fn prints_and_returns_10(a: i32) -> i32 {
    println!("I got the value {}", a);
    10
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn this_test_will_pass() {
        let value = prints_and_returns_10(4);
        assert_eq!(10, value);
    }

    #[test]
    fn this_test_will_fail() {
        let value = prints_and_returns_10(8);
        assert_eq!(5, value); 
    }
}
```

Running this test fails (obviously):

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.30s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 2 tests
test tests::this_test_will_pass ... ok
test tests::this_test_will_fail ... FAILED

failures:

---- tests::this_test_will_fail stdout ----
I got the value 8
thread 'tests::this_test_will_fail' panicked at 'assertion failed: `(left == right)`
  left: `5`,
 right: `10`', src/lib.rs:19:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::this_test_will_fail

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

which also have print statement, `I got the value 8` but for the test that succeded, we don't see any print statement.

<mark class="g">This is because by default standard output is captured for passing tests and we don't see it on the screen. But this behavior can be changed:</mark>

```bash
cargo test -- --show-output
```

which successfully prints our both print statement:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.00s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 2 tests
test tests::this_test_will_pass ... ok
test tests::this_test_will_fail ... FAILED

successes:

---- tests::this_test_will_pass stdout ----
I got the value 4


successes:
    tests::this_test_will_pass

failures:

---- tests::this_test_will_fail stdout ----
I got the value 8
thread 'tests::this_test_will_fail' panicked at 'assertion failed: `(left == right)`
  left: `5`,
 right: `10`', src/lib.rs:19:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::this_test_will_fail

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Running a Subset of Tests
How can we run a subset of tests using test name.

```rust
pub fn add_two(a: i32) -> i32 {
    a + 2
}
 
#[cfg(test)]
mod tests {
    use super::*;
 
    #[test]
    fn add_two_and_two() {
        assert_eq!(4, add_two(2));
    }

    #[test]
    fn add_three_and_two() {
        assert_eq!(5, add_two(3));
    }

    #[test]
    fn one_hundered() {
        assert_eq!(102, add_two(100));
    }
}
```

Say, we wanted to run only one test, specifically the test called `one_hundered()`, here is how we do that:

```bash
cargo test one_hundered
```

then runs only that specific test:

```text
   Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
    Finished test [unoptimized + debuginfo] target(s) in 0.24s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::one_hundered ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 2 filtered out; finished in 0.00s
```

Or run subset of tests by mentioning part of the name:

```bash
cargo test add
```

runs tests starting with `add`:

```text
   Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
    Finished test [unoptimized + debuginfo] target(s) in 0.24s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 2 tests
test tests::add_three_and_two ... ok
test tests::add_two_and_two ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out; finished in 0.00s
```

Notice we have module name `tests` in the tests that were run. So, we can also run tests based on the module it belongs to:

```bash
cargo test tests::
```

runs all test in `tests` module:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.00s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 3 tests
test tests::add_three_and_two ... ok
test tests::add_two_and_two ... ok
test tests::one_hundered ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Ignoring Tests
Ignore tests with `#[ignore]` attribute.

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }

    #[test]
    #[ignore]
    fn expensive_test() {
        // code that takes an hour to run
    }
}
```

Under normal circumstances, running `cargo test` ignore that test case.

But if we do want to run that ignored test case (*only the ignored tests*), we can do as follows:

```bash
cargo test -- --ignore
```

## Test Organization
The Rust community think about test into 2 main categories:
1. **Unit tests**: <mark class="v">Unit tests are small, focused test one module in isolation and could test private interfaces. 
2. **Integration tests**: <mark class="v">Integration tests are completely external to your library and thus test the public interface of your library.

Up until this point, we've writing unit tests and in Rust units tests live in the same file as our product code.

<mark class="y">It's convention that in the same file as your product code, you have a module called `tests` which hold your tests.</mark>

- `cfg` stands for configurtion. With `#[cfg(test)]` means that cargo will only compile this code when we run `cargo test`.
- Even thought the `internal_adder()` is private but we're able to call it inside our test module because of the relationship between the parent and child modules in Rust. Child modules are able to access anything in their parent module, even private fields. 
- Some people in Rust community thinks that it's not right to test private functions, but the functionality is there if the need arises.
- It might look weird to have your test code in the exact same file as your product code. There is a way to keep the tests in separate folder/file but Rust doesn't make this super easy.<mark class="y">Putting the tests inside the same file where the product code resides is the convention.</mark>

```rust
// public function
pub fn add_two(a: i32) -> i32 {
    internal_adder(a, 2)
}

// inner function
fn internal_adder(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn internal() {
        assert_eq!(4, internal_adder(2, 2));
    }
}
```

## Integratinon tests
<mark class="y">Integration tests live in a folder/directory called `tests` at the root of your project.</mark>

Each file in the directory `tests` will be converted to a crate by cargo.

```rust
// tests/integration_test.rs
use adder;

#[test]
fn it_adds_two() {
    assert_eq!(4, adder::add_two(2));
}
```

- Notice at the top of the file we have to bring our `adder` library into scope, because every file in the `tests` directory is going to be a new crate. 
- Then we write our tests, but with no module with `cfg` annotation because Cargo knows that all the files in the test directory are tests.
- Here, we can't call the `inner_adder()`, only public API can be called.

When we test using `cargo test`:

```text
   Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
    Finished test [unoptimized + debuginfo] target(s) in 0.32s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::internal ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running tests/integration_test.rs (target/debug/deps/integration_test-f3950c12fad8757d)

running 1 test
test it_adds_two ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s 
```

This time we have three sections:
- First one for unit tests
- Second one for Integration tests
- Third one for doc tests

To run just our integration tests:

```bash
cargo test --test integration_test
```
---

Because every file in the `tests` directory is treated as a separate crate this could lead to unexpected behavior.

- For example, we have multiple integration test files and we want to share some code between those files. You might do something like this, creating a new file called `tests/common.rs`:

```rust
pub fn setup() {
    // setup code
}
```

running test produces something like this:

```text
   Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
    Finished test [unoptimized + debuginfo] target(s) in 0.23s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::internal ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running tests/common.rs (target/debug/deps/common-b5b22cd1b601f16d)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running tests/integration_test.rs (target/debug/deps/integration_test-f3950c12fad8757d)

running 1 test
test it_adds_two ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

This time we have 4 sections:
- first for unit tests
- next two for integration tests
- last for doc test

So Cargo is treating our `common.rs` file as an integration test file but this is not what we actually wanted to do.

Instead to get the desired behavior create a new folder inside our `tests` directory called `common` and with new file inside that named `mod.rs`; and move our previor `common.rs` file code to this file:

- Also delte the previously created `tests/common.rs`

```rust
// tests/common/mod.rs
pub fn setup() {
    // setup code specific to your library
}
```

Running our test suite again creates expected 3 sections instead of 4 with common code shared between integration tests stored in `tests/common/mod.rs` module:

<mark class="v">This is because file in the subdirectory of the `tests` folder do not compiled as crates.</mark>

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.00s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::internal ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running tests/integration_test.rs (target/debug/deps/integration_test-f3950c12fad8757d)

running 1 test
test it_adds_two ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

So when we want to use our new module of shared code in `integration_test.rs`:

```rust
use adder;

mod common;

#[test]
fn it_adds_two() {
    common::setup();
    assert_eq!(4, adder::add_two(2));
}
```

`mod common;` is module decalration and it will look for the contents of the module in either a file called `common.rs` or a directory named `common` with file named `mod.rs`

One thing to note here is we have a library crate because of `lib.rs`. If we had `main.rs` file we would have a binary crate and we can't directly test binary crate with integration tests. This is why it's common to see a binary crate that's a thin wrapper around a library crate, so that we can test the library crate with integration tests.