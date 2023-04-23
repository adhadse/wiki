# Testing in Rust

Part 1 talk about writing test while the part 2 talk about running, organizing tests into integration tests & unit tests.

!!! info "Why we do even want to write tests?"

    Rust already does a great job of making sure our program is correct with the help of it's type system and borrow checker.

    But these checks can't really test if our functions are really doing the right thing. <mark class="r">Rust just test validity not logic verification.</mark><mark class="g"> Our tests does the logic verification.</mark>

[Writing Automated Tests](https://doc.rust-lang.org/stable/book/ch11-00-testing.html){ .md-button }

## Test Example
To write tests as an example we're going to create a new library called `adder`:

```bash
cargo new adder --lib
cd adder
code .
```

This will create a template library crate with a `lib.rs` file inside `src` directory with an example test function `it_works()` insdie `tests` module:

```rust
#[cfg(test)] // `cfg` means config
mod tests {
  #[test]
  fn it_works() {
    assert_eq!(2 + 2, 4);
  }
}
```

In Rust, functions are tests if they have `#[test]` attribute defined on top. Inside our `tests` module there can be other functions, helper functions not annotated with `#[test]` attribute and hence they'll not be test function.

To run our test, type in terminal:

```bash
cargo test
```

which should give to result something like this:

```
  Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
    Finished test [unoptimized + debuginfo] target(s) in 0.63s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::it_works ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Where we see what tests function where called afte `running 1 test`, theres status, passed or not. In our case it said `ok`. Then we see the summary, if all tests passed then `ok`, how many tests passed, how many failed and so on. In next part we'll also see how we can ignore and filter out tests. The section below that is for document tests. <mark class="y">In Rust we can write tests in our documentation and even test them.</mark>

## Writing a Failing Test
In Rust a test fails when something inside the test function panics. Each test is ran in a new thread and if the main thread sees that the test thread has died then it fails the test.

Let's add a `failing_test()` right below `it_works()` test:

```rust
#[cfg(test)]
mod tests {
    //...

    #[test]
    fn failing_test() {
        panic!("Make this test fail");
    }
}
```

running our updated `lib.rs` with `cargo test`:

```text
  Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
    Finished test [unoptimized + debuginfo] target(s) in 0.33s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 2 tests
test tests::it_works ... ok
test tests::failing_test ... FAILED

failures:

---- tests::failing_test stdout ----
thread 'tests::failing_test' panicked at 'Make this test fail', src/lib.rs:17:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::failing_test

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

This has 2 sections, first shows which tells what tests were ran, then `failures:` section which tells exactly why a test failed, then it lists out failing test and at last summary.

## Testing Product Code
Let's test some actual code. We'll use the code that we wrote in chapter 5 at the top of our `lib.rs` file:

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32
}

impl Rectangle {
    // can this rectanlge hold another recatangle?
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

#[cfg(test)]
mod tests {
    // ...
}
```

Now, let's remove the previous tests and rewrite `tests` module:

- Since our tests are in `tests` module and produce code in default module, we'll bring everything in parent module into scope using `use` keyword.
- <mark class="v">`assert!` macro expects `true/false` to assert that a test pass.</mark>


```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn larger_can_hold_smaller() {
        let larger = Rectangle {
            width: 8,
            height: 7,
        };
        let smaller = Rectangle {
            width: 5,
            height: 1,
        };

        assert!(large.can_hold(&smaller));
    }
}
```

This time our test passes:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.26s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

```

Let's add another test which test a smaller rectangle cannot hold a larger rectangle:

```rust
#[cfg(test)]
mod tests {
    // ...

    #[test]
    fn smaller_cannot_hold_larger() {
        let larger = Rectangle {
            width: 8,
            height: 7,
        };
        let smaller = Rectangle {
            width: 5,
            height: 1,
        };

        assert!(!smaller.can_hold(&larger));
    }
}
```

and this also passes successfully.

Now, let's introduce a bug in our code.

```rust
impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width < other.width && self.height > other.height
        // change first > with < sign
    }
}
```

running our test suite again, fails:

```text
   Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
error[E0425]: cannot find value `large` in this scope
  --> src/lib.rs:29:17
   |
29 |         assert!(large.can_hold(&smaller));
   |                 ^^^^^ help: a local variable with a similar name exists: `larger`

For more information about this error, try `rustc --explain E0425`.
```

## asert_eq! macro
Let's change our `lib.rs` to:

```rust
pub fn add_two(a: i32) -> i32 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_adds_two() {
        assert_eq!(4, add_two(2));
    }
}
```

<mark class="v">The `assert_eq!` macro allow us to compare two value</mark>

This test passes but, if we introduce a bug in our code, let's say add 3 instead of 2:

```rust
pub fn add_two(a: i32) -> i32 {
    a + 3
}
```

fails like this, with `left != right`:

- In Rust we can have the expected value as the right side or left side.

```text
   Compiling adder v0.1.0 (/home/adhadse/Downloads/adder)
    Finished test [unoptimized + debuginfo] target(s) in 0.58s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::it_adds_two ... FAILED

failures:

---- tests::it_adds_two stdout ----
thread 'tests::it_adds_two' panicked at 'assertion failed: `(left == right)`
  left: `4`,
 right: `5`', src/lib.rs:11:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::it_adds_two

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Counter to `assert_eq!` macro is <mark class="v">`assert_ne!` macro which asserts that the two parameter passed in is not equal.</mark>.

One thing to note here <mark class="v">both parameters passed into `assert_eq!` or `assert_ne!` has to implement `PartialEq` and `Debug` traits.</mark>

## Custom Failure Messages
Changing our `lib.rs` to:

```rust
pub fn greeting(name: &str) -> String {
    format!("Hello {}!", name)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn greeting_contains_name() {
        let result = greeting("Carol");
        assert!(result.contains("Carol")); // assert result contains "Carol"
    }
}
```

This test passes. If we modify our `greeting()` function like this:

```rust
pub fn greeting(name: &str) -> String {
    format!("Hello!")
}
```

then the test fails:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.27s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::greeting_contains_name ... FAILED

failures:

---- tests::greeting_contains_name stdout ----
thread 'tests::greeting_contains_name' panicked at 'assertion failed: result.contains(\"Carol\")', src/lib.rs:12:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::greeting_contains_name

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

This output might be okay, but it's not the most useful failure, so let's write our own custom failure message:

```rust
#[test]
fn greeting_contains_name() {
    let result = greeting("Carol");
    assert!(
        result.contains("Carol"),
        "Greeting did not contain name, value was `{}`",
        result
    );
}
```

`assert!` takes a custom failure message as the second parameter, and parameters after that are for the placeholders value in our custom failure message.

Running this update test fails like this:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.29s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::greeting_contains_name ... FAILED

failures:

---- tests::greeting_contains_name stdout ----
thread 'tests::greeting_contains_name' panicked at 'Greeting did not contain name, value was `Hello!`', src/lib.rs:12:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::greeting_contains_name

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Asserting that a Function Panics
We'll learn to write tests that assert a function fails.

In order to our guessing game to work, user needs to provide a value between 1 and 100. If it doesn't, then we need to panic and exit the program. We'll test panic functionality here:

```rust
pub struct Guess {
    value: i32,
}

impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 || value > 100 {
            panic!("Guess value must be between 1 and 100, got {}", value);
        }

        Guess { value }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic]
    fn greater_than_100() {
        Guess::new(200);
    }
}
```

As we can see `greater_than_100()` function is decorated with `#[should_panic]` attribute which asserts that the code inside the function body should panic.

This test also passes sweetly. But if change our `new()` associated function such that it does not panic given the condition we want it to:

```rust
impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!("Guess value must be between 1 and 100, got {}", value);
        }

        Guess { value }
    }
}
```

which fails with message: "test did not panic as expected"

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.24s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::greater_than_100 - should panic ... FAILED

failures:

---- tests::greater_than_100 stdout ----
note: test did not panic as expected

failures:
    tests::greater_than_100

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

error: test failed, to rerun pass `--lib`
```

But can't our function panic for any reason, say other than value being between the range 0 and 100 some other `unwrap()` method calls `panic!`. Our test is just imprecise.

To make assertion a little more precise, we'll make some changes. First let's modify our `new()` function:

```rust
impl Guess {
    pub fn new(value: i32) -> Guess {
        if value < 1 {
            panic!("Guess value must be greater than or equal to 1, got {}", value);
        } else if value > 100 {
            panic!("Guess value must be less than or equal to 100, got {}", value);
        }

        Guess { value }
    }
}
```

and modify `should_panic` attribute to only panic for specific failure message:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "Guess value must be less than or equal to 100")]
    fn greater_than_100() {
        Guess::new(-2); // Notice we use -2
    }
}
```

This says that assert that the code in this test function panics and the failure message is expected to be somethign like that the `expected` argument.

Running our test, this successfully fails:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.24s
     Running unittests src/lib.rs (target/debug/deps/adder-43e1c9247f5d477d)

running 1 test
test tests::greater_than_100 - should panic ... FAILED

failures:

---- tests::greater_than_100 stdout ----
thread 'tests::greater_than_100' panicked at 'Guess value must be greater than or equal to 1, got -2', src/lib.rs:8:13
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
note: panic did not contain expected string
      panic message: `"Guess value must be greater than or equal to 1, got -2"`,
 expected substring: `"Guess value must be less than or equal to 100"`

failures:
    tests::greater_than_100

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

## Returning a Result Type
Tests that return a `Result<T>` type.

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
}
```

Tests that return a `Result<T>` type allows you to use the question mark operator which can be convenient if you have multiple operations withing the test that could return an `Err` type and we want the test to fail if any of those return an error type.
