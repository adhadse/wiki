---
title: "Advanced Traits Rust"
description: "Default Generic Type Parameters, Fully Qualified syntax"
lead: ""
date: 2022-09-20T07:58:28+01:00
lastmod: 2022-09-20T07:58:28+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 32
toc: true
---

## Associated Types
<mark class="v">Associated types are placeholders which we can add to your trait and then methods can use that placeholder.</mark>

```rust
pub trait Iterator {
    type Item;  // associated type named `Item`

    fn next(&mut self) -> Option<Self::Item>;
}

fn main() {}
```

When we implemented our `Iterator` trait, we'll specify a concrete type for `Item`.

<mark class="y">This way we can define a trait which uses some type that's unknown until we implement the trait.</mark>

Like the `next()` method which returns the next item in the iteration, however the type of that item is unknown until the trait is implemented. If the trait is implemented for vector of `i32`, then `Item` will be `i32`.

{{< alert title="Difference between generics and Associated types" type="success" >}}
Although they both allow us to define a type without specifying the concrete value.

<mark class="v">The difference is with associated types we can only have one concrete type per implementation.</mark>

With generics we can have multiple concrete types per implementation.

Let's say we have a struct `Counter` and then we implement `Iterator` trait for our new struct:

```rust
pub trait Iterator {
    type Item;  // associated type named `Item`

    fn next(&mut self) -> Option<Self::Item>;
}

struct Counter {}

impl Iterator for Counter {
    type Item = u32;        // specify associated type

    fn next(&mut self) -> Option<Self::Item> {
        Some(0)             // just an example
    }
}

impl Iterator for Counter {
//^^^^^^^^^^^^^^^^^^^^^^^ error: conflicting implementation of trait `Iterator` for type `Counter`
    type Item = u16;        

    fn next(&mut self) -> Option<Self::Item> {
        Some(0)             
    }
}
```

Here we can't have another implementation where `Item` is something different.

If we use generics instead, and this compiles fine:

```rust
pub trait Iterator<T> {
    fn next(&mut self) -> Option<T>;
}

struct Counter {}

impl Iterator<u32> for Counter {
    fn next(&mut self) -> Option<u32> {
        Some(0)         
    }
}

impl Iterator<u16> for Counter {
    fn next(&mut self) -> Option<u16> {
        Some(0)         
    }
}
```

So when should you use which one?
- **Ask the question to yourself does it make sense to have multiple implementations for a single type or just one implementation.**
{{< /alert >}}

## Default Generic Type Parameters & Operator Overloading
<mark class="v">Generic type parameters could specify a default concrete type allowing implementors to not have to specify a concrete type (unless different from default).</mark>

Great usecase for this is when we need to customize the behavior of an operator, aka, **Operator Overloading**.

Rust allows us to customize the semantics of certain operators that have associated traits in the standard libary's `ops` module.

```rust
use std::ops::Add;

#[derive(Debug, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

// add operator overloading for `Point`
impl Add for Point {
    type Output = Point;

    fn add(self, other: Point) -> Point {
        Point {
            x: self.x + other.x,
            y: self.y + other.y,
        }
    }
}

fn main() {
    assert_eq!(
        Point { x: 1, y: 0 } + Point { x: 2, y: 3},
        Point { x: 3, y: 3}
    );
}
```

If we were to look at the imlementation of the add trait it would look like this:

```rust
// a generic called `Rhs` (Right hand side) with default `Self`
trait Add<Rhs=Self> {  
    type Output;
    
    fn add(self, rhs: Rhs) -> Self::Output;
}
```

Here `Rhs` has default concrete type, `Self` or the type that's implementing the `Add` trait, since if we are going to add two things together, they are probably of same type.

That's why we didn't need to specify concrete type when we implemented `Add` trait for `Point` because `Add` trait has a default concrete type and that will return a `Point`.

What about specifying the type passed into the add method then?

```rust
use std::ops::Add;

struct Millimeters(u32);
struct Meters(u32);

impl Add<Meters> for Millimeters {
    type Output = Millimeters;

    fn add(self, other: Meters) -> Millimeters {
        Millimeters(self.0 + (other.0 * 1000))
    }
}
```

Here, we wanted the `Rhs` generic passed into the `add()` method to be `Meters`. We wanted the ability to add `Meters` to the `Millimeters` and `Millimeters` be returned.

Use default generic type parameters:
1. To extend a type without breaking existing code
2. To allow customization for specific cases which most users won't need.

## Calling Method with the Same Name
Rust allows us to have two traits with same method and implement both those traits on one type.

It's also possible to implement a method on the type itself with the same name as the methods inside the traits. <mark class="y">If we get into the situation where we have the same name then we need to tell Rust which method we'd like to call.</mark>

```rust
trait Pilot {
    fn fly(&self);
}

trait Wizard {
    fn fly(&self);
}

struct Human;

impl Human {
    fn fly(&self) {
        println!("*waving arms furiously*");
    }
}

impl Pilot for Human {
    fn fly(&self) {
        println!("This is you captain speaking.");
    }
}

impl Wizard for Human {
    fn fly(&self) {
        println!("Up!");
    }
}

fn main() {
    let person = Human; // struct has empty fields
    person.fly()
}
```

Running this produces:

```text
*waving arms furiously*
```

which is a method implemented on `Human` struct.

**If we wanted to call `fly()` method from `Pilot` trait or `Wizard` trait then we need syntax like this:**

```rust
fn main() {
    let person = Human; 
    Pilot::fly(&person); // calling `fly()` method of `Pilot` trait
    Wizard::fly(&person); // calling `fly()` method of `Wizard` trait
}
```

produces:

```text
This is you captain speaking.
Up!
```

---

Because `fly()` method takes `self` has a parameter, if we had two different structs which both implemented the `Wizard` trait for example, Rust wouldknow which fly method to call based on the type of `self`.

However this is not true for Associated functions because they don't take `self` as parameter. Let demonstrate that:

```rust
trait Pilot {
    fn fly();
}
 
trait Wizard {
    fn fly();
}
 
struct Human;
 
impl Human {
    fn fly() {
        println!("*waving arms furiously*");
    }
}
 
impl Pilot for Human {
    fn fly() {
        println!("This is you captain speaking.");
    }
}
 
impl Wizard for Human {
    fn fly() {
        println!("Up!");
    }
}
 
fn main() {
    // call associated functions
    Human::fly()
}
```

Running this produces:

```rust
*waving arms furiously*
```

<mark class="v">The associated functions that get's called by default is the associated function on our struct.</mark>

But, what if we wanted to run the associated function defined in implemented traits? For that we need **Fully qualified syntax**:

```rust
fn main() {
    // fully qualified syntax
    <Human as Wizard>::fly()
}
```

updating the main function with this above function produces:

```text
Up!
```

## Supertraits
We may have a trait that's dependent on functionality from another trait, i.e., our trait is dependent on other trait being implemented. In that case the trait we rely is called ***Supertrait***.

For example:

```rust
use std::fmt;

// this print output with surrounding `*`
// **********
// *        *
// * (1, 3) *
// *        *
// **********
trait OutlinePrint {
    fn outline_print(&self) {
        let output = self.to_string(); 
        let len = output.len();
        println!("{}", "*".repeat(len + 4));
        println!("*{}*", " ".repeat(len + 2));
        println!("* {} *", output);
        println!("*{}*", " ".repeat(len + 2));
        println!("{}", "*".repeat(len + 4));
    }
}
```

We'll get an error, because we don't know if `self` the type for which `OutlinePrint` is going to be implemented will implement `to_string()`. This method in implemented in `Display` trait. **Our trait `OutlinePrint` depends on `Display` trat. So we do want to make sure that anything that implements `OutlinePrint` also implements `Display` trait.

To encode this requirement:

```rust
// this trait depends on fmt::Display
trait OutlinePrint: fmt::Display { 
    fn outline_print(&self) {
        let output = self.to_string(); 
        let len = output.len();
        println!("{}", "*".repeat(len + 4));
        println!("*{}*", " ".repeat(len + 2));
        println!("* {} *", output);
        println!("*{}*", " ".repeat(len + 2));
        println!("{}", "*".repeat(len + 4));
    }
}
```

Let's see what happens when we implement this trait on our `Point` struct without implementing `Display` struct on it:

```rust
struct Point {
    x: i32,
    y: i32,
}

impl OutlinePrint for Point {}
//   ^^^^^^^^^^^^ error: `Point` doesn't implement `std::fmt::Display`.
```

We'll get an error, to fix that just implement the `Display` trait:

```rust
impl Dfmt::Display for Point {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "({}, {})", self.x, self.y)
    }
}
```

## Newtype Pattern
We learned about Orphan rule in traits section (Rustlang book, Ch 10).

{{< ref title="Orphan Rule" link="/notes/rust/traits.md" subsection="#orphan-rule" >}}

<mark class="y">The *Newtype pattern* allows us to get around this restriction.</mark> 

<mark class="v">We do this by creating a tuple struct with one field being the type we're wrapping. This wrapper around our type is local to our crate so we can implement a new trait.</mark>

For example, here we want to implement `Display` trait for a vector.

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

which produces:

```text
w = [hello, world]
```

The downside of this pattern is that wrapper is a new type so it's not possible to call method defined on `Vec` type or type stored inside the wrapper directly from Wrapper. However if we did want our new type to implement every method on the type it's holding then we can implement the `Deref` trait such that dereferncing the wrapper return the inner value.

However if we only wanted our new type to have a subset of methods defined on the inner type then we'd have to implement each of those method manually 