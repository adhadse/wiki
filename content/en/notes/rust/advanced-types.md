---
title: "Advanced Types in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:29+01:00
lastmod: 2022-09-20T07:58:29+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 33
toc: true
---

{{< link title="Advanced Types" link="https://doc.rust-lang.org/stable/book/ch19-04-advanced-types.html" >}}

## Newtype Pattern
In previous section we learned about *Newtype Pattern* in the context of implementing a trait on a given type. 

{{< ref title="Newtype Pattern" link="/notes/rust/advanced-traits.md" subsection="#newtype-pattern" >}}

In this example we want to implement `Display` trait on a `Vector` type, however both are defined outisde of our trait. We get around this by defining a new Wrapper type, which a tuple struct containing a vector.

```rust
use std::fmt;
 
struct Wrapper(Vec<String>);
 
impl fmt::Display for Wrapper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "[{}]", self.0.join(", "))
    }
}
 
fn main() {
    let w = Wrapper(
        vec![String::from("hello"), String::from("world")]
    );
    println!("w = {}", w);
}
```

Other uses for *Newtype Pattern* can be to increase type safety.

For example, we have two functions, one function took an age as a paramter and another function took in an employee id as a parameter. <mark class="y">The type of both parameters is `u32`. To avoid mixing of age and employee id when calling the function then we can create a new type which wraps an `u32`.</mark>

Like, we can construct tuple struct for `Age` and `ID`:

```rust
struct Age(u32);
struct ID(u32);
```

Another use of *Newtype Pattern* is to abstract away implementation details.

For example, we can create `People` type which wraps a hash map of integers to strings.

In an essence, *Newtype Pattern* is a lightweight way to achieve encapsulation.


## Type Aliases
Rust also allows to create type aliases to give existing types new names.

```rust
fn main() {
    type Kilometers = i32; // not a new type; just a synonym

    let x: i32 = 5;
    let y: Kilometers = 5;

    println!("x + y = {}", x + y);
}
```

The main usecase of type aliases is to reduce repetition:

```rust
fn main() {
    // `f` of a very lengthy type
    let f: Box<dyn Fn() + Send + 'static> = 
        Box::new(|| println!("hi"));

    fn takes_long_type(f: Box<dyn Fn() + Send 'static>) {
        // --snip--
    }

    fn returns_long_type() -> Box<dyn Fn() + Send + 'static> {
        // --snip--
    }
}
```

Instead of writing this type over and over again, we can create type alias:

```rust
// much easier to read & write
fn main() {
    type Thunk = Box<dyn Fn() + Send + 'static>;

    let f: Thunk = Box::new(|| println!("hi"));

    fn takes_long_type(f: Thunk) {
        // --snip--
    }

    fn returns_long_type() -> Thunk {
        // --snip--
    }
}
```

Type aliases also convey meaning for the type. For example, above here `Thunk` here is a word for code that will be evaluated at some later point.

## Never Type
<mark class="v">The *Never Type* is a special type denoted with `!` meaning that the the function will never return.</mark>

```rust
fn bar() -> ! {
    // --snip--
}
```

Why this might be useful?

Recall that in [Chapter 2](/notes/rust/guessing-game/), we built a guessing game and we had some code which parsed user input into an integer, something like this:

```rust
fn main() {
    while game_in_progress {
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,    
            Err(_) => continue,
        };
    }
} 
```
which took a `guess` and parse it and return a `u32` however if the parsing failed we call `continue` to skip this current iteration.

**But here `guess` is `u32`, so how one `match` arm returns a `u32` and other with `continue`.**

<mark class="g">That's because `continue` has a *Never Type*.</mark> Rust will loook at both arms of this match expression:

```rust
Ok(num) => num,     // return u32
Err(_) => continue, // never type, can never return
```

Thus. Rust confirms that the return type of this expression is an `u32` integer.

<mark class="v">If we get an `Err` variant in the above case, `continue` will not return anything, instead it will move the control back to the top of the loop, never assigning to `guess` and only assigning `u32`.</mark>

---

*Never Type` is useful with `panic!` macro as well.

For example the `Option<T>` enum has a method called `unwrap()` like this which evaluates `self`:

```rust
impl<T> Option<T> {
    pub fn unwrap(self) -> T {
        match self {
            Some(val) => val,  // returns val if `Some` variant
            None => panic!(    // otherwise panic! won't return anything from this function
                "called `Option::unwrap()` on a `None` value" 
            ), 
        }
    }
}
```

`panic!` returns a *Never Type*. 

---

A loop also has *Never Type*

```rust
fn main() {
    print!("forever ");

    loop {
        print!("and over ");
    }
}
```
However this wouldn't be true if we had `break` statement inside of the loop because `break` will cause the loop to terminate.

`print!` is another macro with similar function to `println!` but without any line ending.

## Dynamically Sized Types
<mark class="v">Dynamically Sized Types or Usigned Type are types whose size we can only know at runtime.</mark>

Example of this is `str` type.

```rust
fn main() {
    let s1: str = "Hello there!";
//      ^^ error: the size for values of type `str` cannot be known at compilation time
    let s2: str = "How's it going?";
}
```

For both `s1` and `s2` Rust can't determine the size of these store types at compile time. If we tried to compile this, we'll get the above error.

Instead we need to use borrowed version of `str`, `&str`:

```rust
fn main() {
    let s1: &str = "Hello there!";
    let s2: &str = "How's it going?";
}
```

The string slice `&str` stores two values:
1. An address pointing to the location of string in memory
2. The length of the string

Both the address value and the length of the string have a type of `usize`, we know their size at compile time.

<mark class="y">This is how dynamically sized types are used in Rust.</mark> They have extra data structure which stores the size of the dynamic information.

<mark class="v">The golden rule for DSTs is that we should always put them behind some sort of pointer.</mark>.

In previous example `str` was behind `&` (Reference) but `Box<T>` or `Rc<T>` would also have just worked fine.

### Traits and Dynamically Sized Types
Traits are also Dynamically Sized Types. Traits object always needs to be behind some sort of pointer.

Rust has a special trait called the size trait to determine whether a type `Sized` can be known at compile time or not. The `Sized` trait is autmatically implemented for every type whose size is known at compile time.

Rust implicitly adds the `Sized` trait bound to every generic function.

```rust
fn generic<T>(t: T) {
    // --snip--
}
```

Rust will automatically add `Sized` trait bound like so:

```rust
fn generic<T: Sized>(t: T) {
    // --snip--
}
```

By default generic functions will only work on types whose size is known at compile time, however we ca use the belo syntax to relax this retriction:

```rust
// `T` may be Sized or not 
// Since `T` can be unsized we have to put `T` behind some pointer
fn generic<T: ?Sized>(t: &T) {
```
