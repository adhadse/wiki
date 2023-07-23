# Structs in Rust


Enums and Structs are the building blocks for creating new types.

<mark class="y">Structs allow us to group related data together.</mark> Think about them as object attributes/class attributes in object-oriented programming.

[Using Structs to Structure Related Data](https://doc.rust-lang.org/stable/book/ch05-00-structs.html){ .md-button }

## Using Structs
Let's start with creating a struct for a user.

```rust
struct User {
    username: String, // we want our fields to actually own string data
    email: String,
    sign_in_count: u64,
    active: bool
}

fn main() {
    // create new instance of `User`
    let mut user1 = User {
        email: String::from("happy@gmail.com"),
        username: String::from("Happy"),
        sign_in_count: 1
        active: true,
    }

    // access the fields using dot notation
    let name = user1.username;

    // We can modify specific values in our struct using dot notation
    // But make sure the instance itself is mutable
    user1.username = String::from("wallabag");
}
```

## Function Contructors
We can also use functions to construct new instances of `User`.

```rust
fn main() {
    let user2 = build_user(
        String::from("kevin@gmail.com"),
        String::from("Kevin")
    );


}
fn build_user(email: String, username: String) -> User {
    User {
        email,  // field init shorthand syntax
        username,
        sign_in_count: 1,
        active: true
    }
}
```

## Reusing Instance Data
Create new instances, using existing instances

```rust hl_lines="5"
fn main() {
    let user3 = User {
        email: String::from("daniel@gmail.com"),
        username: String::from("daniel"),
        ..user2   // all other fields assigned from `user2`
    }
}
```

## Tuple Structs
Create structs without named field, called **tuple structs**.
<mark class="y"> Useful when we want our enture tuple to have a name and be of different type than other tuples.

```rust
fn main() {
    // both color and point have the same 3 field types
    // so, if a function expects a tuple type of Color,
    // we can't pass it a tuple of `Point` and vice versa
    struct Color(i32, i32, i32);
    struct Point(i32, i32, i32);
}
```

## Example Use Cases
We'll rewrite this program that calculates the area of rectangle, to understand Structs.

```rust
fn main() {
    let width1 = 30;
    let heigh1 = 50;

    printlln!(
        "The area of the rectangle is {} square units.").
        area(width1, height1)
    );
}

fn area(width: u32, height: u32) -> u32 {
    width * height
}
```

This program works, but could be improved. Let's start grouping the `width` and `height` variable which are related.

```rust
fn main() {
    let rect = (30, 50);

    printlln!(
        "The area of the rectangle is {} square units.").
        area(rect)
    );
}

fn area(dimesions: (u32, u32)) -> u32 {
    dimensions.0 * dimensions.1
}
```

This also works fine. However it's not clear what the fields in the tuple represent. Let's use Structs.

```rust
struct Rectangle {
    width: u32,
    height: u32
}

fn main() {
    let rect = Rectangle { width: 30, height: 50};

    printlln!(
        "The area of the rectangle is {} square units.").
        area(&rect)
    );
}

fn area(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}
```

---
**Derived Traits**
It would be nice to see what our rectangle instances look like. What we want is something like:

```rust
println!("rect: {}", rect);
```
But this doesn't work, because since our custom type doesn't implement `std::fmt::Display` trait, which specifies how something should be printed.

We can however use `{:?}` or `{:#?}` (which prints every field on newline) for pretty print, but requires `Debug` trait to be implemented for the custom type, helpful for developers. We can do this by adding `#[derive(Debug)]` or manually implement `Debug` trait for the struct.

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32
}

fn main() {
    let rect = Rectangle { width: 30, height: 50};
    println!("rect: {:?}", rect);
    ...
```

## Method Syntax
How can we tie closely related functions to an instance of struct, named **methods**, instead of defining separately.

This requires us to use `impl` block which houses methods for a particular Struct.

```rust
impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

fn main() {
    let rect = Rectangle { width: 30, height: 50};
    printlln!(
        "The area of the rectangle is {} square units.").
        rect.area()
    );
}
```

!!! note

    1. The first argument in a method is always `self` which is the instance the method is being called. We can also take a mutable reference, or in rare cases we can can take ownership.
    2. Rust has a feature called autmatic referencing or derefering, which allows us to use dot notation (instead of two different notations, like in C++) on the object directly or calling on the reference of the object.

---

Let's create a method that takes in multiple parameters, called `can_hold`, which takes a reference to another rectangle and determine if the current rectangle instances can hold another rectangel inside itself.

```rust
impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

fn main() {
    let rect = Rectangle { width: 30, height: 50};
    let rect1 = Rectangle { width: 20, height: 40};
    let rect2 = Rectangle { width: 40, height: 50}

    println!("rect can hold rect1: {}", rect.can_hold(&rect1));
    println!("rect can hold rect1: {}", rect.can_hold(&rect2));
}
```

## Associated Functions
<mark class="y">We can also define associated functions inside `impl` block, but unlike methods, they are not tied to an instance of our struct</mark> (think of them static methods).

We can create a new `impl` block to write a associated function that construct a square.

!!! note

    - Notice, there is no `self` argument for associated functions.
    - Use `::` on `Rectangle` struct to call associated functions.
    - We can also use them to write constructors for that type.

```rust
impl Rectangle {
    fn square(size: u32) -> Rectangle {
        Rectangle {
            width: size,
            height: size
        }
    }
}

fn main() {
    let sq = Rectangle::square(25);
}
```
