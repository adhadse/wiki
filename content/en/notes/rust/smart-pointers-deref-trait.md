---
title: "Smart Pointers in Rust - The Deref Trait"
description: ""
lead: ""
date: 2022-09-20T07:58:14+01:00
lastmod: 2022-09-20T07:58:14+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 18
toc: true
---

<mark class="y">The `Deref` trait allows you to customize the behavior of the derefernece operator (`*` before the pointer, e.g. `*y`).</mark>

```rust
fn main() {
    let x = 5; 
    let y = &x;    // `y` is a memory address pointing to memory location where 5 is stored

    assert_eq!(5, x);  // assert 5 is equal to `x`
    assert_eq!(5, *y); // assert derefercing `y` is also equal to 5

    assert_eq!(5, y);   // does `y` is equal to 5?
}
```

Well no, the compiler tells us that:

```text
error[E0277]: can't compare `{integer}` with `&{integer}`
 --> src/main.rs:8:5
  |
8 |     assert_eq!(5, y);   // does `y` is equal to 5?
  |     ^^^^^^^^^^^^^^^^ no implementation for `{integer} == &{integer}`
  |
  = help: the trait `PartialEq<&{integer}>` is not implemented for `{integer}`
  = help: the following other types implement trait `PartialEq<Rhs>`:
            f32
            f64
            i128
            i16
            i32
            i64
            i8
            isize
          and 6 others
  = note: this error originates in the macro `assert_eq` (in Nightly builds, run with -Z macro-backtrace for more info)
```

which indicates we can't compare an integer to a reference to an integer.

Now if we update the above example to use the `Box` smart pointer, the error vanishes:

```rust
fn main() {
    let x = 5; 
    // Box is pointing to value stored somewhere in memory, here 5
    // `y` is pointing to a copy of 5 since it's primitive type
    // since Box type owns the data, instead of transfering the ownership 
    let y = Box::new(x);  

    assert_eq!(5, x);  
    // Since `Box` implements `Deref` trait
    // it allows the derefernce trait to work the same as if it were a reference
    assert_eq!(5, *y); 
}
```
 
## Defining Our own Smart Pointer

```rust
struct MyBox<T>(T);

impl<T> MyBox<T> {
    fn new(x: T) -> MyBox<T> {
        // x is still not stored on Heap though.
        // our focus here is on `Deref` trait
        MyBox(x)  
    }
}

fn main() {
    let x = 5;
    let y = MyBox::new(5);

    assert_eq!(5, x);
    assert_eq!(5, *y);  // error: type `MyBox<{integer}>` cannot be dereferenced
}
```

Since we haven't implemented `Deref` trait yet, we can't use derefernece operator. Continuing the above the code, let add some more pieces:

```rust
use std::ops::Deref;

impl<T> Deref for MyBox<T> {
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
} 
```

Recall that `MyBox` is a tuple struct, so `deref()` method is returning a reference to first item in the tuple (and that's the only item).

Under the hood, Rust actually calls something like this:

```rust
assert_eq(5, *(y.deref()));
```

{{< alert title="Why does the `deref()` returns a reference instead of returning the value itself?" >}}
If `deref()` returned value directly, Rust will move the ownership of the value outside of the smart pointer. Something which we don't really want.
{{< /alert >}}

## Implicit Deref Coercions
Deref Coercion is a convenience feature in Rust that happens automatically for type that implements `Deref` trait which allows <mark class="v">a reference to convert from one type to a reference of different type</mark>.

```rust
fn main() {
    let x = 5;
    let y = MyBox::new(x);

    assert_eq!(5, x);
    assert_eq!(5, *(y.deref()));

    // perfectly fine, even though `hello()` expects a `&str` 
    // and we are passing `&MyBox<String>` 
    // Dereferncing results -> &String which also implements `Deref` trait -> &str
    let m = MyBox::new(String::from("Rust"));
    hello(&m);
}

fn hello(name: &str) {
    println!("Hello, {}!", name);
}
```

## Deref Coercion and Mutability
Rust can automatically perform these chained deref calls at compile time to get the correct type.

Rust does deref coercion when it finds types and trait implementations in three cases:

- From `&T` to `&u` when `T: Deref<Target=U>`
- From `&mut T` to `&mut U` when `T: DerefMut<Target=U>`
- From `&mut T` to `&U` when `T: Deref<Target=U>`

{{< alert type="warning" >}}
Rust cannot perform Deref coercion when going from an immutable reference to mutable reference due to borrowing rules:
- We can only have one mutable reference to a specific piece of data withing a specific scope.
{{< /alert >}}