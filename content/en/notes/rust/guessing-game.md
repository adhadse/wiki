---
title: "Programming a guessing game in Rust"
description: ""
lead: ""
date: 2022-09-20T07:55:56+01:00
lastmod: 2022-09-20T07:55:56+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 2
toc: true
---

Let's create a new project by using `Cargo` and open the dir in editor:
{{< link title="Guessing Game" link="https://doc.rust-lang.org/stable/book/ch02-00-guessing-game-tutorial.html" >}}

```bash
cargo new guessing-game
```

And edit `src/main.rs`:

```rust
fn main() {
    println!("Guess the number!");
    println!("Please input your guess.");
    let guess = String::new();
}
```
`String is a UTF-8 encoded, growable string from standard library. `new()` is an associative function on `String` which returns an empty string.

You IDE would probably infer the type of `guess` and annotate it with String. You can annotate your variable explicitly like this:

```rust
let guess: String = String::new();
```

<mark class="y">One thing to note here is that unlike C++/C, in Rust variables are immutable by default.</mark> So our `guess` variable still ain't ready to mutate and store any input and change value from default string. Let's change that in the original code:

```rust
fn main() {
    println!("Guess the number!");
    println!("Please input your guess.");

    // a mutable `guess`
    let mut guess = String::new();
}
```

## I/O
Standard I/O operations can be supported using by io module in `std` (standard) library. Let's *use* it by adding it to top of our code:

```rust
use std::io;

fn main() { ...
```
We can now create a handle to the standard input of the current process using `stdin` function. `read_line()` will take the input and store in passed `buf` variable which is supposed to be a *mutable reference* to String (in our case `guess`). This allows us to modify it without changing ownership of string. We'll talk about this in depth later:

```rust
    let mut guess = String::new();

    io::stdin()
        .readline(&mut guess)
}
```

`readline()` returns an Enum [`std::result::Result`](https://doc.rust-lang.org/std/result/) type:

```rust
pub enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

`Result` is a type that represent either *variant*success (`Ok`) or *variant* failure (`Err`).

So to handle the error, we can use the `expect()` to indicate any error msg otherwise print out the guess variable:

```rust
    io::stdin()
        .read_line(&mut guess)
        .expect("Failed to read line");

    println!("You guessed: {}", guess);
```

## Random Number Generation
To generate random numbers we'll need to add a depedency to our `Cargo.toml` file since `std` library don't ship with one:

```toml
[dependencies]
rand = "0.5.5"
```
After that run `cargo build` command, which will compile and bring any new dependecies as described by `Cargo.toml` and also other libs that the new dependency depends on.

Let "import" this dependency as we learned previously, or in Rust terms, *bring into scope of current file*. We'll be bringing `Rng` trait from `rand` library which defines methods that random number generators.

```rust
use std::io;
use rand::Rng;

fn main() { ...
```

Let's create a new variable to store our randomly generated number and check it's value by running our program using command `cargo run`:

```rust
fn main() {
    println!("Guess the number");
    
    // gen_range generates a number between 1 and 100
    let secret_number = rand::thread_rng().gen_range(1..101);
    println!("The secret number is: {}", secret_number);
    ...
}
```

If we wanted to create inclusive range we could have done something like this:

```rust
let secret_number = rand::thread_rng().gen_range(1..=100);
```

## Compare the guess and secret_number

To do that let's bring `Ordering` into scope. `Ordering` is an enum that is a result of two things being compared, viz: `Less`, `Equal`, `Greater`:

```rust
use std::io;
use std::cmp::Ordering;
...
```

Continuing at the bottom, we'll use `cmp()` at match all possible variants of `Ordering` enum using `match` keyword:

```rust
    println!("You guessed: {}", guess);

    match guess.cmp(&secret_number) {
        Ordering::Less => println!("Too small!"),
        Ordering::Greater => println!("Too bug!"),
        Ordering::Equal => println!("You win!"),
    }
}
```

**But**, this will give an error since `guess` is of type `String` whereas `secret_number` is an `int`. So we'll need to convert our `guess` to `int`.

```rust
    // perform this just after read_line() 
    // shadowing `guess` of type String
    let guess: u32 = guess.trim().parse()
        .expect("Please type a number");

```

## Game Loop
Let's add a loop, so that user can keep guessing until they get the right number.

```rust
fn main() {
    loop {
        println!("Guess the number!");
        // gen_range generates a number between 1 and 100
        let secret_number = rand::thread_rng().gen_range(1..101);
        println!("The secret number is: {}", secret_number);
        
        println!("Please input your guess.");
    
        // a mutable `guess`
        let mut guess = String::new();
        
        io::stdin()
            .read_line(&mut guess)
            .expect("Failed to read line");
        let guess: u32 = guess.trim().parse()
            .expect("Please type a number");
    
        println!("You guessed: {}", guess);
        
        match guess.cmp(&secret_number) {
            Ordering::Less => println!("Too small!"),
            Ordering::Greater => println!("Too bug!"),
            // exit loop if found the match
            Ordering::Equal => {
                println!("You win!");
                brak;
            },
        }
    }
}
```

Ok, that's almost done!

## Handling invalid inputs
Currently, our program panics if we user gives String as input. We want user to keep prompting to input a number instead of panicking.

We can modify our `parse()` when parsing `guess` from `String` to `u32` as it returns a `Result` enum which can be either `Ok` or `Err` with `_` to catch any err value and continue no matter what.

```rust
    let guess: u32 = match guess.trim().parse() {
        Ok(num) => num,
        Err(_) => continue,
    }
```