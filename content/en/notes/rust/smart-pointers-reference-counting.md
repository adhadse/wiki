---
title: "Smart Pointers in Rust - Reference Counting"
description: ""
lead: ""
date: 2022-09-20T07:58:16+01:00
lastmod: 2022-09-20T07:58:16+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 20
toc: true
---

There are some cases where a single value has multiple owners, for e.g., a graph with multiple edges that point to same node, the node being owned by those edges. So the node should not be cleaned up until it doesn't have any edges pointing to it.

<mark class="v">To enable multiple ownership of a value we can use a reference counting smart pointer which keeps tracks of number of references to a value and when there are no more references the value will get cleaned up.</mark>

<mark class="r">Reference counting smart pointers we'll discuss here are only useful for single threaded applications.</mark> For multi-threaded we'll discuss later on.

{{< link title="Rc<T>, the Reference Counted Smart Pointer" link="https://doc.rust-lang.org/stable/book/ch15-04-rc.html" >}}

## Using Rc to Share Data
We'll be demonstrating the use of `Rc` using Cons list as we discussed earlier.

```rust
use crate::List::{Cons, Nil};


enum List {
    Cons(i32, Box<List>),
    Nil,
}

fn main() {
    let a = Cons(5, Box::new(Cons(10, Box::new(Nil))));
    let b = Cons(3, Box::new(a));
    let c = Cons(4, Box::new(a));  // error: use of moved value: `a`
}
```

The `Cons` variants holds the data they hold, on line 10 when we created `b` it owned `a`, hence the value now cannot be owned by `c` on line 11.

We can though change the definition of `Cons` variant to hold references instead of owned value, but that would require the use of lifetimes. Using lifetimes we would specify that every element in the list as to live at least as long as long as the entire list.

This is because, the borrow checker would'nt allow the code to compile because a temporary `&Nil` would be dropped before `a` could take a reference to it.

We can adapt the `Cons` variant to use a reference counting pointer, instead of a `Box` pointer:

```rust
use std::rc::Rc;
use crate::List::{Cons, Nil};

enum List {
    Cons(i32, Rc<List>),
    Nil,
}

fn main() {
    // we'll also need to wrap the list inside `a` with Rc because 
    // we're passing it into `b` and `c` 
    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));

    // to pass `a` to `b` and `c`, we'll use `Rc::clone()`
    let b = Cons(3, Rc::clone(&a));
    let c = Cons(4, Rc::clone(&a));  
}
```

<mark class="v">`Rc::clone()` doesn't create deep copies of the data. It only increments the reference count.</mark>.

Another way to do this is to:

```rust
let b = Cons(3, a.clone());
```

although in our case the convention is to use the first syntax: `Rc::clone(&a)`.

**We can't pass in a reference to `a` here since we expect it to be a owned type:**

```rust
let b = Cons(3, &a);
```

We also can't pass `a` directly, since that would mean move of ownership:

```rust
let b = Cons(3, a);
```

## Increasing the Reference Count
Let's see how the reference count changes as we create new `List` and updated Reference count.
```rust
use std::rc::Rc;
use crate::List::{Cons, Nil};
 
enum List {
    Cons(i32, Rc<List>),
    Nil,
}
 
fn main() {
    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));
    println!("count after creating a = {}", Rc::strong_count(&a));  // not weak count

    let b = Cons(3, Rc::clone(&a));
    println!("count after creating b = {}", Rc::strong_count(&a));
    {
        // inner scope
        let c = Cons(4, Rc::clone(&a));
        println!("count after creating c = {}", Rc::strong_count(&a));
    }

    println!("count after c goes out of scope = {}", Rc::strong_count(&a));
}
```

results in:

```text
count after creating a = 1
count after creating b = 2
count after creating c = 3
count after c goes out of scope = 2
```

{{< alert type="warning" >}}
Note that the reference counting smart pointer only allows multiple parts of our program to read the same data **not modify it**.

This is due to multiple mutable references violates borrowing rules. There could only be one mutable reference to a value.
{{< /alert >}} 
