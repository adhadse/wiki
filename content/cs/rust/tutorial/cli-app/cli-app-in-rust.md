# CLI App in Rust

We'll be creating a simple clone of a popular command line tool called ***grep*** which basically allows us to search for a string withing a file. We'll call our project `minigrep`.

[An I/O Project: Building a Command Line Program](https://doc.rust-lang.org/stable/book/ch12-00-an-io-project.html){ .md-button }

## Accepting Command Line Arguments
We want the user to pass in a string and a file name, which we'll accept via command line arguments to our program.

- For that we'll import `env` module and create a variable called `args`. `args()` function gives us an iterator over the arguments passed to our program and collect function will turn that iterator into a collection. That's why we needed to specify the type for `args` variable.
- Then we'll print our arguments

```rust
// src/main.rs
use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    println!("{:?}", args);
}
```

Running this with `cargo run` prints one argument by default when we don't pass in any arguments which is the path to our binary:

```text
  Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.62s
     Running `target/debug/minigrep`
["target/debug/minigrep"]
```

Let's try passing in some arguments:

```bash
cargo run needle haystack
```
produces:

```text
    Finished dev [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/minigrep needle haystack`
["target/debug/minigrep", "needle", "haystack"]
```

We only care about query and filename, so we'll create two variables to store them.

```rust
fn main() {
    let args: Vec<String> = env::args().collect();

    // reference of element at index 1, index 0 is just binary path
    let query = &args[1];
    let filename = &args[2];

    println!("Searching for {}", query);
    println!("In file {}", filename);
}
```

and passing in query and filename as arguments: `cargo run test sample.txt`

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.26s
     Running `target/debug/minigrep test sample.txt`
Searching for test
In file sample.txt
```

## Reading a File
Let's create a new file at the root of our project called `poem.txt` with some beautiful poem in it:

> A poem by Emily Dickinson

```text
I'm nobody! Who are you?
Are you nobody, too?
Then there's a pair of us - don't tell!
They'd banish us, you know.

How dreary to be somebody!
How public, like a frog
To tell your name the livelong day
To an admiring bog!
```

So how are we going to read the contents of the file? We'll use `fs` module from `std`:

- The `read_to_string()` returns a string by reading a file wrapped in `Result<T>` type. If it returns an `Err` variant we want to exit our program, so we use `expect()` method on top to print a message while panicking.

```rust
use std::env;
use std::fs;

fn main() {
    // ...
    println!("In file {}", filename);

    let contents = fs::read_to_string(filename)
        .expect("Something went wrong readint the file");

    // if everything else goes successfully
    println!("With text:\n{}", contents);
}
```

Let's run our program by giving it the filename and query: `cargo run the poem.txt`:

```text
    Finished dev [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/minigrep the poem.txt`
Searching for the
In file poem.txt
With text:
I'm nobody! Who are you?
Are you nobody, too?
Then there's a pair of us - don't tell!
They'd banish us, you know.

How dreary to be somebody!
How public, like a frog
To tell your name the livelong day
To an admiring bog!
```

## Refactoring
There are few things we could improve:
- Our main function does two things: it is reponsible for parsing arguments as well as reading the cotents of a file. Ideally we want function (even main function) to have one responsibility, i.e., keep the reposnibility of a function scoped.
- We also have these two arguments `query` and `filename` connected, but that connection isn't expressed in our program.
- When we read the contents of the file and it fails our message simply says "Something went wrong reading the file". The message is more or less useless in describing what actually went wrong.
- We also don't have a centralized place to handle errors. The function can fail when wrong no of arguments are passed or when there is some problem when reading a file.

<mark class="y">The pattern to follow when `main()` of binary crate has too many responsibilites developed by Rust community is to create a library crate and then have the binary crate call the function in the library crate.</mark>

But before that let's extract out some logic:


```rust
// main.rs
use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();

    let (query, filename) = parse_config(&args);

    println!("Searching for {}", query);
    println!("In file {}", filename);

    let contents = fs::read_to_string(filename)
        .expect("Something went wrong readint the file");

    println!("With text:\n{}", contents);
}

fn parse_config(args: &[String]) -> (&str, &str) {
    // reference of element at index 1, index 0 is just binary path
    let query = &args[1];
    let filename = &args[2];

    (query, filename)
}
```

- Now even though we have extracted the logic, the two string represent the  `query` and `filename` but it's still not very clear that these two string are connected.

To fix that problem let's create a struct called `Config`:

```rust
// main.rs
// ...

fn main() {
    let args: Vec<String> = env::args().collect();

    let config = parse_config(&args);

    println!("Searching for {}", config.query);
    println!("In file {}", config.filename);

    let contents = fs::read_to_string(config.filename)
        .expect("Something went wrong readint the file");

    println!("With text:\n{}", contents);
}

struct Config {
    query: String,
    filename: String
}

fn parse_config(args: &[String]) -> Config {
    // we could use lifetimes to make thing effecient but for now this is easier.
    let query = args[1].clone();
    let filename = args[2].clone();

    Config { query, filename }
}
```

Still our `parse_config()` is tied to our config struct but our program doesn't express this coupling. What we need is an associated function for `Config` named `new()` to generate a `Config` object (a convention for constructor function):

```rust
// main.rs
// ...

fn main() {
    let args: Vec<String> = env::args().collect();

    let config = Config::new(&args);

    // ...
}

struct Config {
    // ...
}

impl Config {
    fn new(args: &[String]) -> Config {
        let query = args[1].clone();
        let filename = args[2].clone();

        Config { query, filename }
    }
}
```

Now let's fix error handling. If we don't pass enough arguments to our program (`cargo run`), the error message is not so useful or straight away confusing for user to understand what the program expects:

```text
   Finished dev [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/minigrep`
thread 'main' panicked at 'index out of bounds: the len is 1 but the index is 1', src/main.rs:26:21
```

We need more better error message:

```rust
// main.rs
// ...

impl Config {
    fn new(args: &[String]) -> Config {
        if args.len() < 3 {
            panic!("not enough arguments");
        }

        let query = args[1].clone();
        let filename = args[2].clone();

        Config { query, filename }
    }
}
```

which should now output if we don't pass enough arguments:

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.35s
     Running `target/debug/minigrep`
thread 'main' panicked at 'not enough arguments', src/main.rs:27:13
```

But the error still contains a lot more information not so useful to a user. That's because we are calling `panic!` macro.<mark class="g"> `panic!` is much more useful when we have a programming error rather than a usage error.</mark>

Let's fix this by:
- Returning a `Result<T>` by our `new()` function of `Config` with Config in `Ok` case or a `&str` (string slic) in the `Err` case representing error message.
- And instead or panicking return an `Err` type.
- Plus import `process` to help us exit program without panicking.

We'll use `unwrap_or_else()` to handle our `Err` case passing in a closure.

[Closures](/cs/rust/functional/closures/){ .md-button }

```rust
use std::env;
use std::fs;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();

    // this will return `config` in `Ok` case or print err and exit program
    let config = Config::new(&args).unwrap_or_else(|err| {
        println!("Problem parsing arguments: {}", err);
        process::exit(1); // pass in status code 1
    });

    // ...
}

// ...

impl Config {
    fn new(args: &[String]) -> Result<Config, &str> {
        if args.len() < 3 {
            return Err("not enough arguments");
        }

        let query = args[1].clone();
        let filename = args[2].clone();

        Ok(Config { query, filename })
    }
}
```

Running this produces a much nicer, readable output with `cargo run`:

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.25s
     Running `target/debug/minigrep`
Problem parsing arguments: not enough arguments
```

---

Next, we'll create a function named `run()` which will contain logic that doesn't have to do with setting up the configuration or handling errors but is only repsonsible for reading the contents of the file and printing it out:

- Also return a `Result<T>` instead of panicking when something goes wrong while reding the file. In the success case  we return a *Unit* type `()` and in `Err` case we return `Error`. the `Box<dyn Error>` just means return any type of error.

```rust
// imports ...
use std::error:: Error;

fn main() {
    // ...

    // Delete this section in main
    // let contents = fs::read_to_string(config.filename)
    //     .expect("Something went wrong readint the file");

    // println!("With text:\n{}", contents);

    // since we only care about `Err` variant
    if let Err(e) = run(config) {
        println!("Application error: {}", e);
        process::exit(1);
    }
}

fn run(config: Config) -> Result<(), Box<dyn Error>> {
    // the `?` immediately return with the Error from the function if this result in Err
    let contents = fs::read_to_string(config.filename)?;

    println!("With text:\n{}", contents);

    Ok(()) // Return `Ok` variant passing in Unit `()`
}

// ...
```

Running this program for a file that doesn't exist return:

```text
    Finished dev [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/minigrep the file.txt`
Searching for the
In file file.txt
Application error: No such file or directory (os error 2)
```
