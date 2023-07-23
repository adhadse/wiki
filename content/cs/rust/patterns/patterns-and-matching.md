# Patterns and Matching in Rust

!!! info "What are patterns?"

    Patterns are special syntax in Rust for matching against the structure of types.

    Patterns consist of some combination of following:
    - Literals
    - Destructed
        - Arrays
        - Enums
        - Structs
        - Tuples
    - Variables
    - Wildcards
    - Placeholders

These components describe the shape of the data we're working with which we can then match against values to determine whether out program has the correct data to continue running or not.

[Patterns and Matching](https://doc.rust-lang.org/stable/book/ch18-00-patterns.html){ .md-button }

## match Arms
We already know to use patterns inside `match` expressions:

```rust
fn main() {
    enum Language {
        English,
        Spanish,
        Russian,
        Japanese,
    }

    let language = Language::English;

    // a match arm
    match language {
        // patterns => expressions,
        Language::English => println!("Hello World!"),
        Language::Spanish => println!("Hola Mundo!"),
        // _ => println!("Unsupported language!")
    }
}
```

`match` expressions should be exhaustive, i.e., every possible value for the variable has to be accounted for.

That's why the above program does not compile due to non-exhaustive patterns, we've not added `Language::Russian` and `Language::Japanese`. We could add that but there is another way to fix this using a catch-all pattern:

```rust
_ => println!("Unsupported language")
```

So, if our program goes through all of these arms and none of them matches, then we execute the catch-all arm (it doesn't need to be at the end always).

The underscore (`_`) doensn't bind to the variable we're matching on. If we did want to bind to the variable, we could do:

```rust
lang => println!("Unsupported language! {:?}", lang)
```

## Conditional if-let Expressions
You use `if-let` expressions if you want to match on some variable but you only care about one case.

[Using if let Syntax](/cs/rust/enums-and-pattern-matching/#using-if-let-syntax){ .md-button }

This piece code determines users's authorization status.


```rust
fn main() {
    let authorization_status: Option<&str> = None; // Option containing "string slice"
    let is_admin = false;
    let group_id: Result<u8, _> = "34".parse(); // Result containing either `u8` or error

    if let Some(status) = authorization_status {
        println!("Authorization status: {}", status);
    } else if is_admin {
        println!("Authorizatin status: admin");
    } else if let Ok(group_id) = group_id {
        if group_id > 30 {
            println!("Authorization status: priviledge");
        } else {
            println!("Authorization status: basic");
        }
    } else {
        println!("Authorization status: guest");
    }
}
```

The downside of `if-let` expressions is that the compiler doesn't enfore that they are exhaustive, i.e., you can get away with not writing last `else` case.

## While let Conditional Loops
while-let loop allows us to continue the loop as long as the pattern specified continues to match.

```rust
fn main() {
    let mut stack = Vec::new();

    stack.push(1);
    stack.push(2);
    stack.push(3);

    while let Some(top) = stack.pop() {
        println!("{}", top);
    }
}
```

## for loops
Use pattern to destructure the tuple into two variables.

```rust
fn main() {
    let v = vec!['a', 'b', 'c'];

    // for PATTERN in variable { }
    for (index, value) in v.iter().enumerate() {
        println!("{} is at index {}", value, index);
    }
}
```

## let Statements

```rust
fn main() {
    let x = 5;

    // let PATTERN = EXPRESSION

    let (x, y, z) = (1, 2, 3); // to destruct; since pattern match 3 variables

    // But...
    let (x, y) = (1, 2, 3);
    //  ^^^^^^ error: mismatched types
    //  expected tuple `({integer}, {integer}, {integer})` found tuple `(_, _)`

    // use _ to ignore values
    let (x, y, _) = (1, 2, 3);
}
```

## Function Parameters

```rust
fn main() {
    let point = (3, 5); // you do require brackets to identify as tuple
    print_coordinates(&point);
}

// decontruct tuple into `x` and `y`.
fn print_coordinates(&(x, y): &(i32, i32)) {
    println!("Current location: ({}, {})", x, y);
}
```

## Irrefutable and Refutable patterns
<mark class="v">Irrefutable patterns are those patterns that will always match</mark>

<mark class="v">Refutable patterns might not match.</mark>

Only accept irrefutable patterns:
- function parameters
- let statements
- for loops

if-let and while-let expressions accepts both refutable and irrefutable patterns but we'll get a compiler warning if we use an irrefutable pattern because those expressions are meant to handle matching failures.


```rust
fn main() {
    // Irrefutable
    let x = 5;

    // Refutable
    let x: Option<&str> = None;
    if let Some(x) = x {
        println!("{}", x);
    };
}
```
