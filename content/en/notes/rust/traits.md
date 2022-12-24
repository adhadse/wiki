---
title: "Traits in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:03+01:00
lastmod: 2022-09-20T07:58:03+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 11
toc: true
---

<mark class="v">Traits define shared behavior for structs.</mark>

{{< link title="Traits: Defining Shared Behavior" link="https://doc.rust-lang.org/stable/book/ch10-02-traits.html" >}}

## Defining Traits
Let's look at the below code:

```rust
pub struct NewsArticle {
    pub author: String,
    pub headline: String,
    pub content: String,
}

pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}
```

We want is the ability to summarize a news article or a Tweet, so that we can post it in text aggregation feed of our system.

We can use Trait to define that shared behavior between `NewsArticle` and `Tweet` to summarize.

<mark class="v">Traits allow us to define a set of methods that are shared across different types. Every type that implements this trait should have the method defined in the trait.</mark>

```rust
pub trait Summary {
    fn summarize(&self) -> String;
}
```

Implement `Summary` trait for `NewsArticle` and `Tweet`
```rust
pub struct NewsArticle {
    pub author: String,
    pub headline: String,
    pub content: String,
}

// then we'll implement `Summary` trait for `NewsArticle`
impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {}", self.headline, self.author)
    }
}
```

```rust
pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}
```

Let's write the main function and try running this:

```rust
fn main() {
    let tweet = Tweet {
        username: String::from("@johndoe"),
        content: String::from("Hello World!"),
        reply: false,
        retweet: false
    };
    let article = NewsArticle {
        author: String::from("John Doe"),
        headline: String::from("The Sky is Falling"),
        content: String::from("The sky is not actually falling.")
    };

    println!("Tweet summary: {}", tweet.summarize());
    println!("Article summary: {}", article.summarize());
}

```

Outputs:

```text
Tweet summary: @johndoe: Hello World!
Article summary: The Sky is Falling, by John Doe
```

### Orphan Rule
<mark class="v">We can implement a trait on a type as long as the trait or the type is defined within the crate.</mark>

This rule ensures that other people’s code can’t break your code and vice versa. Without the rule, two crates could implement the same trait for the same type, and Rust wouldn’t know which implementation to use.

## Default Implementations
Instead of expecting every type that implements a trait to define the body of the those functions, we can (when needed) specify the default implementation which can be overrided.

```rust
pub trait Summary {
    fn summarize(&self) -> String {
        String::from("(Read more...)")
    }
}
```

When you don't want to override the default implementation just specify that the type implement the trait, and only override the function that you want to:

```rust
impl Summary for NewsArticle {}
```

Now the program outputs:

```text
Tweet summary: @johndoe: Hello World!
Article summary: (Read more...)
```

---
Default implementations can other methods inside our trait definition:

```rust
pub trait Summary {
    fn summarize_author(&self) -> String;

    fn summarize(&self) -> String {
        format!("(Read more from {}...)", self.summarize_author())
    }
}
```

Now we do need to implement `summarize_author()` for both `NewsArticle` and `Tweet` but not `summarize()` for `NewsArticle` as it follows default implementation:

```rust
impl Summary for NewsArticle {
    // no `summarize()`; default implementation for that
    
    fn summarize_author(&self) -> String {
        format!("{}", self.author)
    }
}
```

```rust
impl Summary for Tweet {
    fn summarize_author(&self) -> String {
        format!("@{}", self.username)
    }

    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}
```

This changes the output for `NewsArticle`

```text
Tweet summary: @johndoe: Hello World!
Article summary: (Read more from John Doe...)
```

## Trait Bounds
<mark class="v">Using Traits as parameters.</mark>

Check the code below, which follows our summarization system above:

```rust
// `notify()` has one parameter `item` which is a reference
// to something that implements `Summary` trait
pub fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize())
}
```

Now in the main function:

```rust
fn main() {
     let article = NewsArticle {
        author: String::from("John Doe"),
        headline: String::from("The Sky is Falling"),
        content: String::from("The sky is not actually falling.")
    };

    notify(&article);
}
```

Outputs:

```text
Breaking news! (Read more from John Doe...)
```

### Trait Bound Syntax
This works for straightforward cases but's it's actually syntax sugar for something called **Trait Bound**, which looks like this:

```rust
// T generic limited to somthing that implements `Summary` trait
pub fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize())
}
```

---
Let's look at more complex cases. What if we wanted `item1` and `item2` to be exactly same syntax:

```rust
// impl syntax: nah. this syntax won't work
// `item1` and `item2` can be two different type both implementing `Summary` trait
pub fn notify(item1: &impl Summary, item2: &impl Summary) {
    // ...
}

// Trait Bound syntax: yup. 
// `T` generic will now be same type that implements `Summary` trait
pub fn notify<T: Summary>(item1: &T, item2: &T) {
    // ...
}
```

### Specifying multiple Traits
We can also specify multiple traits:

```rust
// Something which implements both `Summary` and `Display` trait
pub fn notify(item: &(impl Summary + Display), item2: &impl Summary) {
    // ...
}

pub fn notify<T: Summary + Display>(item1: &T, item2: &T) {
    // ...
}
```

### Fixing Readability
Specifying trait bounds can hinder readability

```rust
fn some_function<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) -> i32 {
    // ...
}
```

<mark class="g">To fix this we can use `where` clause</mark>:

```rust
fn some_function<T, U>(t: &T, u: &U) -> i32 
where T: Display + Clone,
        U: Clone + Debug 
{

}
```

## Returning Types the Implement Traits
Following the original example, we can return only **one** type that implements a trait, useful in iterators and closures.

```rust
pub trait Summary {
    fn summarize_author(&self) -> String;
 
    fn summarize(&self) -> String {
        format!("(Read more from {}...)", self.summarize_author())
    }
}

// returning any type that implements `Summry` trait; not a concrete type
fn returns_summarizable() -> impl Summary {
    Tweet {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        retweet: false,
    }
}

fn main() {
    println!("{}", returns_summarizable().summarize());
}
```

Outputs:

```text
horse_ebooks: of course, as you probably already know, people
```

{{< alert type="warning" title="We can only return one type" >}}
This is not allowed. This has to do with how the compiler implements the `impl` syntax.

```rust
fn returns_summarizable(switch: bool) -> impl Summary {
    if switch {
        NewsArticle {
            headline: String::from(
                "Penguins win the Stanley Cup Championship!",
            ),
            author: String::from("Iceburgh"),
            content: String::from(
                "The Pittsburg Penguins once again are the best \
                hockey team in the NHL.",
            ),
        }
    } else {
        Tweet {
            username: String::from("horse_ebooks"),
            content: String::from(
                "of course, as you probably already know, people",
            ),
            reply: false,
            retweet: false,
        }
    }
}
```

Compiler will complain:

```text
error[E0308]: `if` and `else` have incompatible types
```
{{< /alert >}}

## Conditionally Implement Methods 

```rust
use std::fmt::Display;

struct Pair<T> {
    x: T,
    y: T,
}

// every `Pair` struct will have `new()` associative function
impl<T> Pair<T> {
    fn new(x: T, y: T) -> Self {
        Self { x, y }
    }
}

// however `cmp_display()` method is only available to `Pair` 
// structs where the type of `x` and `y` implements `Display`
// `PartialOrd` traits
impl<T: Display + PartialOrd> Pair<T> {
    fn cmp_display(&self) {
        if self.x >= self.y {
            println!("The largest member is x = {}", self.x);
        } else {
            println!("The largest member is y = {}", self.y);
        }
    }
}
```

## Blanket Implementations
<mark class="y">We can implement a trait on a type that implements another trait.</mark>

```rust
// implement `ToString` trait on any type `T` that implements 
// `Display` trait
impl<T: Display> ToString for T {
    // ...
}
```

## Difference between self and Self

{{< alert type="success" title="Difference between `self` and `Self`?" >}}
<mark class="v">[Self](https://doc.rust-lang.org/reference/types.html#self-types) is the type of the current object.</mark> It may appear either in a `trait` or an `impl`, but appears most often in `trait` where it is a stand-in for whatever type will end up implementing the `trait` (which is unknown when defining the trait):

```rust
trait Clone {
    fn clone(&self) -> Self;
}
```
Implement `Clone`:

```rust
impl Clone for MyType {
    // I can use either the concrete type (known here)
    fn clone(&self) -> MyType;

    // Or I can use Self again, it's shorter after all!
    fn clone(&self) -> Self;
}

// or 
impl Clone for MyType {
    fn new(a: u32) -> Self {
        // ...
    }
}
```
---

<mark class="v">`self` is the name used in a `trait` or an `impl` for the first argument of a method.</mark> Using another name is possible, however there is a notable difference:

- <mark class="y">if using self, the function introduced is a method</mark>
- <mark class="v">if using any other name, the function introduced is an associated function</mark>

In Rust, there is no implicit this argument passed to a type's methods: we have to explicitly pass the "current object" as a method parameter. This would result in:

```rust
impl MyType {
    fn doit(this: &MyType, a: u32) { ... }
}

// but we can write the shorter way
impl MyType {
    fn doit(&self, a: u32) { ... }
}
```

So, basically:

```rust
self => self: Self
&self => self: &Self
&mut self => self: &mut Self
```

Source:  [What's the difference between self and Self?](https://stackoverflow.com/a/32310313/8277795) (Stack Overflowra)
{{< /alert >}}