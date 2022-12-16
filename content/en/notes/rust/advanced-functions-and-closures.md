---
title: "Advanced Functions and Closures in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:30+01:00
lastmod: 2022-09-20T07:58:30+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 34
toc: true
---

{{< link title="Advanced Functions and Closures" link="https://doc.rust-lang.org/stable/book/ch19-05-advanced-functions-and-closures.html" >}}

## Function Pointers
We can also pass functions to functions, like passing closures to functions.

This is useful when we want to pass a function we already defined instead of creating a new closure.

To pass in a function as an argument, we can use a function pointer specified using `fn`:

```rust
fn add_one(x: i32) -> i32 {
    x + 1
}

// `f` accept a function with one input i32 and returns i32
fn do_twice(f: fn(i32)) -> i32, arg: i32) -> i32 {
    f(arg) + f(arg)
}

fn main() {
    let answer = do_twice(add_one, 5);

    println!("The answer is: {}", answer);
}
```

<mark class="v">Unlike closures `fn` is a type rather than a trait.</mark> So, we can use `fn` directly.

If we recall from Closures section:
{{< ref title="fn traits" link="/notes/rust/closures.md" subsection="#generic-parameters-and-fn-traits" >}}

there are three closure traits:

1. `Fn`: specifies that the closure the variables in its environment immutably
2. `FnMut`: specifies the closure capture the variables in its environment mutably
3. `FnOnce`: specifies that the closure takes ownership of the values in its environment (thus cosuming the variables)

<mark class="v">Function pointers implement all these three closure traits.</mark>

<mark class="y">i.e., if we have a function that expects a closure, we can pass it a closure or function pointer.</mark> That's why it's preferable to write function that expects a closure instead of just pointer type.

In above code we can update `do_twice()` function to take either closure or function like this:

```rust
// 1. specify generic
// 2. change f: T
// 3. Introduce trait bound using `Fn`
fn do_twice<T>(f: T, arg: i32) -> i32 
where T: Fn(i32) -> i32 {
    f(arg) + f(arg)
}
```

<mark class="v">**`Fn` is closure trait bound whereas `fn` which is a function pointer type.**</mark>

The case in which we may only want to accept function pointer instead of functions pointers and closures is if you're interfacing with external code that does not support closures. `C` functinos don't closures.

---

Another example where we can use closure or predefined function:

```rust
fn main() {
    let list_of_numbers = vec![1, 2, 3];
    let list_of_strings: Vec<String> = 
        list_of_numbers
            .iter()
            .map(|i| i.to_string()) // map takes closure or function pointer called for every int
            .collect();
    println!("{:?}", list_of_strings);
}
```

To pass in a function pointer to `map()` method, we can do using *fully qualified syntax*:

```rust
// passing `to_string()` method on ToString trait
// because there can be other method named `to_string` in this scope
.map(ToString::to_string)
```

---

Anoter useful pattern that exploits an implementation detail of tuple structs and tuple struct enum variants.

```rust
fn main() {
    enum Status {
        Value(u32),
        Stop,
    }
}
```

Tuple struct uses parantheses `()` to initialize values inside the tuple struct which looks like function call.

Actually these initializers are implemented as functions that take in arguments and return an instance of that tuple struct.

That means we can use these initializers as function pointers:

```rust
// creating vector of Statuses 
// by calling map on range passing in `Value` variant
// map treats `Value` as a function pointer with argument being `u32`
// return value being `Value` variant
let list_of_statuses: Vec<Status> = 
    (0u32..20).map(Status::Value).collect();

```

Obviously closures can also be passed in.

## Returning Closures
Returning closures from functions.

```rust
fn returns_closure() -> {
    |x| x + 1
}
```

This function returns a closure, but it's unfinished. Closures are represented using traits, so the function won't return a concrete type.

What we want to say is we want to return something that implements the `Fn` trait taking in an integer and returning an integer.

```rust
fn returns_closure() -> impl Fn(i32) -> i32 {
    |x| x + 1
}
```

The above syntax might not work in all situation. For example, like in this where we return a closue based on input argument:

```rust
fn returns_closure(a: i32) -> impl Fn(i32) -> i32 { // this syntax only work when returning one type
    if a > 0 {
        move |b| a + b
    } else {
        move |b| a - b
      //^^^^^^^^^^^^^^ error: no two closures, even if identical have same type  
      // consider boxing your closure and/or using it as a trait object
    }
}
```

So instead, we need to return a trait object, wrapped in smart pointer so compiler can know it's size  like this:

```rust
fn returns_closure(a: i32) -> Box<dyn Fn(i32) -> i32> { 
    if a > 0 {
        Box::new(move |b| a + b)
    } else {
        Box::new(move |b| a - b)
    }
}
```