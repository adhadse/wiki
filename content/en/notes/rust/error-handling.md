---
title: "Error Handling in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:01+01:00
lastmod: 2022-09-20T07:58:01+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 9
toc: true
---

{{< link title="Error Handling" link="https://doc.rust-lang.org/stable/book/ch09-00-error-handling.html" >}}

## Using panic!
If your program fails in a way that's unrecoverable or there is no way to handle the error gracefully, then you can call the panic macro, which immediately quit the program.

```rust
fn main() {
    panic!("crash and burn");
}
```

Which crashes:
```text
thread 'main' panicked at 'crash and burn', src/main.rs:2:5
```

If we wanted to get a full backtrace of where and in which function did the panic originated, like in this case, we can run with `RUST_BACKTRACE=full` environment variable set as:

```bash
RUST_BACKTRACE=full cargo run
```

```rust
fn main() {
    a();
}

fn a() {
    b();
}

fn b() {
    c(22);
}

fn c(num: i32) {
    if num == 22 {
        panic!("Don't pass in 22!");
    }
}
```

which emits,
```text
thread 'main' panicked at 'Don't pass in 22!', src/main.rs:15:9
stack backtrace:
   0: rust_begin_unwind
             at /rustc/a55dd71d5fb0ec5a6a3a9e8c27b2127ba491ce52/library/std/src/panicking.rs:584:5
   1: core::panicking::panic_fmt
             at /rustc/a55dd71d5fb0ec5a6a3a9e8c27b2127ba491ce52/library/core/src/panicking.rs:142:14
   2: playground::c
             at ./src/main.rs:15:9
   3: playground::b
             at ./src/main.rs:10:5
   4: playground::a
             at ./src/main.rs:6:5
   5: playground::main
             at ./src/main.rs:2:5
   6: core::ops::function::FnOnce::call_once
             at /rustc/a55dd71d5fb0ec5a6a3a9e8c27b2127ba491ce52/library/core/src/ops/function.rs:248:5
```

## The Result Enum
Errors that are recoverable and can be handled gracefully, in those cases the result is required to be wrapped inside `Result` enum:

```rust
enum Result<T, E> {
    Ok(T),   // success case, contains result
    Err(E),  // error case
}
```

The `Result` enum represent <mark class="g">success or failure</mark>

--- 
For example:

```rust
use std::fs::File;

fn main() {
    // calling `File::open()` may fail incase file not existing
    // and hence it returns a `Result` enum; annotated just for clarity
    let f: Result<File, Error> = File::open("hello.txt");

    // We must handle both the cases of `Result` using `match`
    // shadowing to declare f
    let f = match f {
        Ok(file) => file,
        Err(error) => panic!("Problem opening the file: {:?}",error)
    };
}
```

Let's handle it more gracefully by instead of panicking, create a new file:

First bring `ErrorKind` struct from `io` module into scope, <mark class="y">which let us match on the type of errror we get.</mark>

```rust
use std::fs::File;
use std::io::ErrorKind;
```

and then match on the error we get instead of calling `panic!` macro:

```rust
let f = match f {
        Ok(file) => file,
        Err(error) => match error.kind() {
            // which returns an enum representing the kind of error
            // creating a new file can also fail, so match expression for that
            ErrorKind::NotFound => match File::create("hello.txt") {
                Ok(fc) => fc,
                Err(e) => panic!("Problem creating the file: {:?}", e)
            },
            other_error => {
                panic!("Problem opening the file: {:?}", other_error)
            }
        }
    };
```

--- 
This looks not so pretty, so we can rewrite the above code using closures, which we'll learn more about later.

```rust
use std::fs::File;
use std::io::ErrorKind;

// `unwrap_or_else()` gives use file or call the anonymous 
// function / closure passing in `error`
// inside the closue we have if-else statement; 
// - first checking error is created for file not found 
//   - if yes, then try creating the file which itself can fail
//   - in that case, we have another closure binding error and panicking
// - otherwise, for any other error, we just panic
fn main() {
    let f = File::open("hello.txt").unwrap_or_else( |error| {
        if error.kind() == ErrorKind::NotFound {
            File::create("hello.txt").unwrap_or_else( |error| {
                panic!("Problem creating the File: {:?}", error);
            })
        } else {
            panic!("Problem opening the file: {:?}", error);
        }
    });
}
```

### Useful functions on Result Enum
We can simplify our original code of `match` expression and `panic` by calling <mark class="v"> `unwrap()` which panics or return the result</mark>:

```rust
use std::fs::File;

fn main() {
    // unwrap does the same thing
    // - in success case, return item stored in `Ok` varient
    // - otherwise, in `Err` case panic
    let f = File::open("hello.txt").unwrap();
}
```

We can <mark class="v">use `expect()` method which let us specify the error message or panics.</mark>

```rust
use std::fs::File;

fn main() {
    let f = File::open("hello.txt").expect("Failed to open Hello.txt");
}
```

## Error Propagation
Often times, we want to give more control to the caller function of what to do with the error, i.e., <mark class="y">we want to return an error instead of handling it ourselves. This is known as Error propagation.</mark>

```rust
use std::fs::File;
use std::io;
use std::io::Read;

// this function returns a `Result` type returning the file content
// or an `io::Error`
fn read_username_from_file() -> Result<String, io::Error> {
    let f = File::open("hello.txt");

    // opening file can fail, in which case we return an error
    let mut f = match f {
        Ok(file) => file,
        Err(e) => return Err(e)
    }

    // otherwise we read content in String `s` and return `s`
    let mut s = String::new();
    match f.read_to_string(&mut s) {
        Ok(_) => Ok(s),
        Err(e) => Err(e)
    }
}
```

## The ? Operator
We can simplify this further,<mark class="v"> by adding `?` to the call of the `open()` method, which gives the unwrapped item otherwise in case of error it returns early with the error</mark>:

```rust
use std::fs::File;
use std::io;
use std::io::Read;

fn read_username_from_file() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;

    // opening file can fail, in which case we return an error
    // let mut f = match f {
    //     Ok(file) => file,
    //     Err(e) => return Err(e)
    // }

    // let mut s = String::new();
    // match f.read_to_string(&mut s) {
    //     Ok(_) => Ok(s),
    //     Err(e) => Err(e)
    // }
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}
```

We can simplify even further by **chaining method calls**

```rust
use std::fs::File;
use std::io;
use std::io::Read;

fn read_username_from_file() -> Result<String, io::Error> {
    let mut s = String::new();
    File::open("hello.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
```

Or maybe even further,

```rust
use std::fs::{self, File};
use std::io;
use std::io::Read;

fn read_username_from_file() -> Result<String, io::Error> {
    fs::read_to_string("hello.txt")
}
```

--- 
**What happens if we try to use `?` in our main function?**

{{< alert >}}
The `main()` can returning Nothing, or a `Result` type.
{{< /alert >}}

```rust
use std::error::Err;
use std::fs::File;

fn main() {
    // error!
    // error[E0277]: the `?` operator can only be used in a
    // function that returns `Result` or `Option` (or another 
    // type that implements `FromResidual`)
    let f = File::open("hello.txt")?;
}
```

So we can change this to return a `Result` type:

```rust
use std::error::Err;
use std::fs::File;

// In success case, we return `()` unit
// in error case we return a trait object (any type of error)
fn main() -> Result<(), Box<dyn Error>> {
    let f = File::open("hello.txt")?;

    Ok(())
}
```

{{< alert title="When to use panic or Result enum" type="success" >}}
In general, by default you should be using `Result` enum and Error propagation. This prevents your program from crashing while the caller function to handle the error as per requirement.

The `panic!` should be reserved for exceptional circumstances where recovering from error is not possible. 
- Another place where `panic!` is in example code where there is not context on how to deal with error.

You can also use `unwrap()` or `expect()` in prototype phase code, after which you might want to consider error handling for all such calls.
- `unwrap()` and `expect()` could also be used in test code, because we want the test to fail if we expected the code to succeed fails to do so.
- or use `unwrap()` and `expect()` when you know your call to a function will succeed.

```rust
use std::net::IpAddr;

fn main() {
    let home: IpAddr = "127.0.0.1".parse().unwrap();
}
```
{{< /alert >}}