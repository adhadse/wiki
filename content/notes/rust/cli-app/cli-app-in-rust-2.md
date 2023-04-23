# CLI App in Rust - Part 2

[Developing the Library’s Functionality with Test-Driven Development](https://doc.rust-lang.org/stable/book/ch12-04-testing-the-librarys-functionality.html){ .md-button }

## Test Driven Development
Let's move our `run()`, `Config` struct and it's `impl` block into a library crate and declutter our `main.rs`.

Create a `src/lib.rs`.

```bash
nano src/lib.rs
```

And move those functions we discssed above in this file (and also move relevant import statements):

- We'll also want to make our `run()` function, `Config` struct and it's fields as well as `new()` associated function in `Config`'s `impl` block public so that anything outside our library crate can use that.

```rust
// src/lib.rs
use std::fs;
use std::error::Error;

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.filename)?;

    println!("With text:\n{}", contents);

    Ok(())
}

pub struct Config {
    pub query: String,
    pub filename: String
}

impl Config {
    pub fn new(args: &[String]) -> Result<Config, &str> {
        if args.len() < 3 {
            return Err("not enough arguments");
        }

        let query = args[1].clone();
        let filename = args[2].clone();

        Ok(Config { query, filename })
    }
}
```

Now in `main.rs` we're going to import these and use them:

```rust
// src/main.rs
use std::env;
use std::process;

use minigrep::Config; // import with `minigrep`; the name of our crate

fn main() {
    let args: Vec<String> = env::args().collect();

    let config = Config::new(&args).unwrap_or_else(|err| {
        println!("Problem parsing arguments: {}", err);
        process::exit(1); // pass in status code 1
    });

    println!("Searching for {}", config.query);
    println!("In file {}", config.filename);

    // use minigrep::run()
    if let Err(e) = minigrep::run(config) {
        println!("Application error: {}", e);
        process::exit(1);
    }
}
```

Now let's test this out with `cargo run the poem.txt`

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.70s
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

And it compiles successfully and runs just as fine!

### Writing tests
We'll write a test that fails then implement the logic that'll make the test pass and if necessary refactor our code and make sure our test is still passing.

- Currently, our program just spits out the content of the file. Instead we want it to search for query string inside the file and only print out line that contain our query. For that we'll create a function `search()` but before as said, we'll write a test to test that functionality (which obviously will fail since the functionality isnt't implemented yet).

```rust
// src/lib.rs
impl Config {
    // ...
}

pub fn search(query: &str, contents: &str) -> Vec<&str> {
//             error: missing lifetime specifier  ^
// this function's return type contains a borrowed value but the signature
// does not say whether it is borrowed from `query` or `contents`.
    vec![]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_result() {
        let query = "duct";
        let contents = "\
Rust:
safe, fast, productive.
Pick three.";

        assert_eq!(vec!["safe, fast, productive."], search(query, contents));
    }
}
```

For the above error, we know how to fix it, by specifying the lifetimes associated for the output value with one the input parameters:

!!! info

    Anytime we return a reference from a function we have to tie the lifetime of that reference to the lifetime of one of the input parameters.

<mark class="y">So we want the returned vector to have a lifetime tied to the `contents` input parameter, because retrun strings will simply be lines inside the contents string.</mark>

```rust
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    vec![]
}
```

Now if we run `cargo test`, as expected the tests fails:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.44s
     Running unittests src/lib.rs (target/debug/deps/minigrep-41ffe2f4028fe4d9)

running 1 test
test tests::one_result ... FAILED

failures:

---- tests::one_result stdout ----
thread 'tests::one_result' panicked at 'assertion failed: `(left == right)`
  left: `["safe, fast, productive."]`,
 right: `[]`', src/lib.rs:44:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::one_result

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

```

Let's write test that will make this test pass:

```rust
// search() return a Vec of string, where each string is a line which
// contains our query
pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    let mut results = Vec::new();

    for line in contents.lines() {
        if line.contains(query) {
            results.push(line);
        }
    }

    results
}
```

now, if we run our test, we get passing test:

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished test [unoptimized + debuginfo] target(s) in 0.35s
     Running unittests src/lib.rs (target/debug/deps/minigrep-41ffe2f4028fe4d9)

running 1 test
test tests::one_result ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/debug/deps/minigrep-1d6aff2511469b21)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests minigrep

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

```

Now, let's use our tested `search()` function inside `run()` function:

```rust
// src/lib.rs
pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.filename)?;

    // println!("With text:\n{}", contents);
    for line in search(&config.query, &contents) {
        println!("{}", line);
    }

    Ok(())
}
```

When we run our program: `cargo run the poem.txt`:

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.37s
     Running `target/debug/minigrep the poem.txt`
Searching for the
In file poem.txt
Then there's a pair of us - don't tell!
```

If we test it for a query that doesn't exist: `cargo run dog poem.txt`, we get 0 line print out:

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.37s
     Running `target/debug/minigrep the poem.txt`
Searching for dog
In file poem.txt
```

## Environment Variables
Currently our `search()` function logic is case sensitive, so we'll add an option to perform case insensitive searching, but instead of using command line arguments we'll use environment variables (to learn about them).

So, again let's write a new test for case insensitivity that for now fails:

- Also change first test case name from `one_test()` to `case_sensitive()`.

```rust
// src/lib.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    // fn one_result() {
    fn case_sensitive {    // change first test case name
        let query = "duct";

        // and add one more line to make sure the function
        // don't return last line since it contains `Duct` for case sensitive case.
        let contents = "\
Rust:
safe, fast, productive.
Pick three.
Duct tape.";
        // ...
    }

    #[test]
    fn case_insensitive() {
        let query = "rUsT";
        // two occurence first line: `Rust` and last line in `Trust`
        let contents = "\
Rust:
safe, fast, productive.
Pick three.
Trust me.";

        assert_eq!(
            vec!["Rust:", "Trust me."],  // we expect this function to return
            search_case_insensitive(query, contents)
        );
    }
}
```

Now, let's define `search_case_insensitive()` right above our `tests` module:

```rust
// src/lib.rs
pub fn search_case_insensitive<'a>(
    query: &str,
    contents: &'a str,
) -> Vec<&'a str> {
    vec![]
}
```

Running our test now outputs:

```text
    Finished test [unoptimized + debuginfo] target(s) in 0.53s
     Running unittests src/lib.rs (target/debug/deps/minigrep-41ffe2f4028fe4d9)

running 2 tests
test tests::case_sensitive ... ok
test tests::case_insensitive ... FAILED

failures:

---- tests::case_insensitive stdout ----
thread 'tests::case_insensitive' panicked at 'assertion failed: `(left == right)`
  left: `["Rust:", "Trust me."]`,
 right: `[]`', src/lib.rs:60:9
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::case_insensitive

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

And as expected `case_sensitive` test pass, but `case_insensitive` test fails.

Let's implement our `search_case_insensitive()` function to make this failing test pass.

```rust
// src/lib.rs

// converts query and line to lowercase and then search
pub fn search_case_insensitive<'a>(
    query: &str,
    contents: &'a str,
) -> Vec<&'a str> {
    let query = query.to_lowercase();
    let mut results = Vec::new();

    for line in contents.lines() {
        // line.to_lowercase() returns new string, so no
        // modification to what would be actually printed.
        if line.to_lowercase().contains(&query) {
            results.push(line);
        }
    }

    results
}
```

Running our test now, everything passes:

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished test [unoptimized + debuginfo] target(s) in 0.69s
     Running unittests src/lib.rs (target/debug/deps/minigrep-41ffe2f4028fe4d9)

running 2 tests
test tests::case_insensitive ... ok
test tests::case_sensitive ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

     Running unittests src/main.rs (target/debug/deps/minigrep-1d6aff2511469b21)

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s

   Doc-tests minigrep

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

But how would our program figure out which search function to use? We'll use environment variables.

Let's update our `Config` struct to account for case sensitivity for a search:

- replace our `run()` to use case_sensitive field, looping over `results`
- Bring `env` module into scope
- modify `new()` function on `Config`

```rust
use std::fs;
use std::error::Error;
use std::env;

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.filename)?;

    // call differnt function depending on Config.case_sensitive
    let results = if config.case_sensitive {
        search(&config.query, &contents)
    } else {
        search_case_insensitive(&config.query, &contents)
    }

    // loop over results
    for line in results {
        println!("{}", line);
    }
}

pub struct Config {
    // ...
    pub case_sensitive: bool
}

impl Config {
    pub fn new(args: &[String]) -> Result<Config, &str> {
        if args.len() < 3 {
            return Err("not enough arguments");
        }

        let query = args[1].clone();
        let filename = args[2].clone();
        // `is_err()` returns a bool; if not set set to false otherwise true
        let case_sensitive = env::var("CASE_INSENSITIVE").is_err();

        Ok(Config { query, filename, case_sensitive })
    }
}

// ...
// ...
```

Let's try this out: `cargo run to poem.txt`

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.33s
     Running `target/debug/minigrep to poem.txt`
Searching for to
In file poem.txt
Are you nobody, too?
```

And when we export our expect env variable:

```bash
export CASE_INSENSITIVE=true
```

and then test, `cargo run to poem.txt`

```text
    Finished dev [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/minigrep to poem.txt`
Searching for to
In file poem.txt
Are you nobody, too?
How dreary to be somebody!
To tell your name the livelong day
```

and again we can uset the environment variable:

```bash
uset CASE_INSENSITIVE
```

## Writing to Standard Error
Lastly, we'll change our `main()` function to print errors to standard error instead of standard output.
- Command line programs are expected to send errors to the standard error stream so that if the user wanted to say, send output stream to a file they would still see errors on the screen.

Let's see what happens when we stream output to a file:

```bash
cargo run > output.txt
```

It doesn't output anything to terminal but in our file, all errors are written out:

```text
    Finished dev [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/minigrep`
```

```text
Problem parsing arguments: not enough arguments
```

To fix this just replace `println!` with `eprintln!` for errors:

```rust
// src/main.rs
use std::env;
use std::process;

use minigrep::Config; // import with `minigrep`; the name of our crate

fn main() {
    let args: Vec<String> = env::args().collect();

    let config = Config::new(&args).unwrap_or_else(|err| {
        eprintln!("Problem parsing arguments: {}", err);   // eprintln!
        process::exit(1); // pass in status code 1
    });

    println!("Searching for {}", config.query);
    println!("In file {}", config.filename);

    // use minigrep::run()
    if let Err(e) = minigrep::run(config) {
        eprintln!("Application error: {}", e);            // eprintln!
        process::exit(1);
    }
```

This time if we run the previous command, we do see output. And `output.txt` is empty

```text
   Compiling minigrep v0.1.0 (/home/adhadse/Downloads/minigrep)
    Finished dev [unoptimized + debuginfo] target(s) in 0.26s
     Running `target/debug/minigrep`
Problem parsing arguments: not enough arguments
```

And with correct arguments standard output is directed to `output.txt` and no errors are printed out to standard error strem (in terminal) `cargo run to poem.txt > output.txt`:

```text
    Finished dev [unoptimized + debuginfo] target(s) in 0.00s
     Running `target/debug/minigrep to poem.txt`
```

and `output.txt` is:

```text
Searching for to
In file poem.txt
Are you nobody, too?
How dreary to be somebody!
To tell your name the livelong day
To an admiring bog!
```
