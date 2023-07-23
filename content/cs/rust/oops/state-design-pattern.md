# State Design Pattern in Rust

[Implementing an Object-Oriented Design Pattern](https://doc.rust-lang.org/stable/book/ch17-03-oo-design-patterns.html){ .md-button }

## Object Oriented Design Pattern
In the state pattern we have some value which has internal state represented by *state objects*.

Each *state object* is reponsible for its own behavior and deciding when to transition into another state.

The value that holds the state objects know nothing about the different behavior states or when to transition into different state.

<mark class="g">The benefit is that when the business requirement change, we don't need to change the code which uses the value but instead we need to change code inside one of the *state objects* or add new *state objects*</mark>

To understand this pattern, we'll be implementing a blog post workflow in Rust.

The workflow is kinda like this:

- A blog post start as empty draft
- After drafting a review is done
- Once it gets approved and then published post return content to be print

Also some sequence is also required. Like, if somebody tries to review a post before a review is requested then that blog post should remain in a draft state.

The workflow should look something like this in code, in a new library crate named `blog`:

```rust
// main.rs
use blog::Post;

fn main() {
    let mut post = Post::new();

    post.add_text("I ate a salad for lunch today");
    assert_eq!("", post.content());  // In draft state post will be empty

    post.request_review();
    assert_eq!("", post.content()); // post will still be empty because it's not approved

    // upon approve, `post.content()` should return actual content of the post
    post.approve();
    assert_eq!("I ate a salad for lunch today", post.content());
}
```

Interation here is done with `Post` type. The `Post` type will store a value representing the state of the post which is either:

- Draft
- Waiting for review or
- Published

and this state transition is managed by the `Post` type upon invocation of methods.

## Defining Post
Inside `src/lib.rs`:

```rust
// lib.rs
pub struct Post {
    state: Option<Box<dyn State>>,
    content: String,
}

impl Post {
    pub fn new() -> Post {
        // a constructor function with
        // `state` set to `Draft` and `content` empty
        Post {
            state: Some(Box::new(Draft {})),
            content: String::new(),
        }
    }
}

// `State` trait define shared behavior
// between various state of a post
trait State {}

// later we'll define other states as well
struct Draft {}

impl State for Draft {}
```

## Storing Text
We'll need to implement `add_text()` method that update the post `content` since the field is private.

```rust
// lib.rs
impl Post {
    pub fn new() -> Post {
        Post {
            state: Some(Box::new(Draft {})),
            content: String::new(),
        }
    }

    // a `mut` reference to `self` to mutate `content`
    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text)
    }
}
```

`add_text()` is a  functionality we want but doens't depend on what state the post is in; and hence not part of state pattern.

## Content Method

```rust
// lib.rs
impl Post {
    pub fn new() -> Post {
        Post {
            state: Some(Box::new(Draft {})),
            content: String::new(),
        }
    }

    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text)
    }

    // this should only return if `Post` is published
    // But since we have now only implemented `Draft` state.
    // We simply return an empty String
    pub fn content(&self) -> &str {
        ""
    }
}
```

## Requesting a Review
First we'll add a new state called `PendingReview` at the end of the file `lib.rs`:

```rust
struct PendingReview {}

impl State for PendingReview {}
```

Then we'll define a new method on `State` trait called `request_review() which takes ownerhsip of `Self` and returns a `State` trait object:

Remember why we want to return a trait object:

[Trait for common behavior](/cs/rust/oops/trait-objects/#trait-for-common-behavior){ .md-button }

```rust
trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
}
```

and then we'll add a custom implementation for both `Draft` and `PendingReview`:

```rust
struct Draft {}

impl State for Draft {
    // this will take ownership of `Box<T>` containing `Self
    // and there is no `Self` inside the function; we're invalidating &
    // returning a new state in it's place
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        Box::new(PendingReview {})
    }
}
```

```rust
struct PendingReview {}

impl State for PendingReview {
    // doens't require anything to do since it's already in PendingReview
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        self
    }
}
```

At last let's implement a public `request_review()` method on `Post` struct:

```rust
impl Post {
    pub fn new() -> Post {
        Post {
            state: Some(Box::new(Draft {})),
            content: String::new(),
        }
    }

    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text)
    }

    pub fn content(&self) -> &str {
        ""
    }

    pub fn request_review(&mut self) {
        // `take()` the value out of the Option, leaving a `None` in its place
        // and that what we are matching onto on the left side of if-let statement
        if let Some(state) = self.state.take() {
            self.state = Some(state.request_review());
        }
    }
}
```

The `request_review()` method on `Post` struct is going to be same no matter what state we're in. Each state is responsible for it's own rules that govern what happend when we call `request_review()` on that particular *state object*.

## Adding the approve Method
Before we add `approve()` method to `Post` struct, we'll add a new `Published` state struct at the end of `lib.rs`.

```rust
struct Published {}

impl State for Published {
    // if post is already Published just return this state
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        self
    }
}
```

Then we'll add new method to `State` trait:

```rust
trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
    fn approve(self: Box<Self>) -> Box<dyn State>;
}
```

Then we'll implement this method for `Draft` stuct:

```rust
impl State for Draft {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        // ...
    }

    // return self because approval won't work until review is requested
    fn approve(self: Box<Self>) -> Box<dyn State> {
        self
    }
}
```

Same goes for `Published` *state object*:

```rust
impl State for Published {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        // ...
    }

    // approval isn't required since Post is already published
    fn approve(self: Box<Self>) -> Box<dyn State> {
        self
    }
}
```

But for `PendingReview` state, we want to transition to `Published` state:

```rust
impl State for PendingReview {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        // ...
    }

    // approval isn't required since Post is already published
    fn approve(self: Box<Self>) -> Box<dyn State> {
        Box::new(Published {})
    }
}
```

At last we're going to add `approve()` method to `Post` struct:

```rust
impl Post {
    // ...

    pub fn approve(&mut self) {
       if let Some(state) = self.state.take() {
            self.state = Some(state.approve());
        }
    }
}
```
---

We'll also want `Post` struct to return content of the post if it is in `Published` state.

So let's update the `content()` method of `Post` struct:

```rust
impl Post {
    // ...

    pub fn content(&self) -> &str {
        self.state.as_ref().unwrap().content(self)
    }

    // ...
}
```

We're calling `as_ref()` because `state` is going to be an `Option<T>` that owns the state object but instead we want reference to the state object. Because we know that there's always going to be a valid `State` object it's safe to call `unwrap()` to get the inside value of `Some` variant.

Then we call the `content()` method (not yet implemented though) on state object, passing in `post` (which is `self`).

<mark class="y">The goal is to keep all these rules contained within the *state objects* sot the `content()` method takes a reference to the `Post` so that it has access to the `content` field on the `Post` and can return appropriate string depending upon state.</mark>

Because of Deref coercion we were able to call `content()` method directly, even though `as_ref()` returns an `Option<T>` that contains a reference to `Box<T>` holding the state object: `Option<&Box<dyn State, Global>>`.

---

Now, let's implement the `content()` method for each State, but before that again we update our trait `State` with the new method with a default implementation.

```rust
trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
    fn approve(self: Box<Self>) -> Box<dyn State>;
    fn content(&self, post: &Post) -> &str {
        ""
    }
}
```

Now we'll only add custom implementation for `PublishedState` since it is the only one which should return `content`.

```rust
impl State for Published {
    // ...
    fn content(&self, post: &Post) -> &str {
        &post.content
    //  ^^^^^^^^^^^^^ error: this parameter and the return type are declared with different lifetimes...
    }
}
```

So, we're taking in two references and returning another reference. We want to tell the compiler the relationship between input parameters's lifetimes and returned parameter lifetime. Essentially we want `&content` to live as long as `post` argument.

So using lifetimes:

```rust
impl State for Published {
    // ...
    fn content<'a>(&self, post: &'a Post) -> &'a str {
        &post.content
    }
}
```

and also update `State` trait signature:

```rust
trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
    fn approve(self: Box<Self>) -> Box<dyn State>;
    fn content<'a>(&self, post: &'a Post) -> &'a str {
        ""
    }
}
```

## Trade-offs of the State Pattern
One downside here is that some state are coupled to each other.

For example, imagine we want to add a state between `PendingReview` and `Published`, say `Scheduled`.

After adding that state, we would need to update the `PendingReview` state such that when `approve()` is called it transitions to `Scheduled` state.

The other downside is duplication. We've very similar implementation for `request_review()` and `approve()` in `impl` block for `Post` struct. We could use macros to reduce those repetition in case we had larger codebase.

### Final lib.rs

At the end the `lib.rs` should look something like this:

```rust
// lib.rs
pub struct Post {
    state: Option<Box<dyn State>>,
    content: String,
}

impl Post {
    pub fn new() -> Post {
        Post {
            state: Some(Box::new(Draft {})),
            content: String::new(),
        }
    }

    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text)
    }

    pub fn content(&self) -> &str {
        self.state.as_ref().unwrap().content(self)
    }

    pub fn request_review(&mut self) {
       if let Some(state) = self.state.take() {
            self.state = Some(state.request_review());
        }
    }

    pub fn approve(&mut self) {
       if let Some(state) = self.state.take() {
            self.state = Some(state.approve());
        }
    }
}

trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
    fn approve(self: Box<Self>) -> Box<dyn State>;
    fn content<'a>(&self, post: &'a Post) -> &'a str {
        ""
    }
}

// later we'll define other states as well
struct Draft {}

impl State for Draft {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        Box::new(PendingReview {})
    }

    fn approve(self: Box<Self>) -> Box<dyn State> {
        self
    }
}

struct PendingReview {}

impl State for PendingReview {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        self
    }

    fn approve(self: Box<Self>) -> Box<dyn State> {
        Box::new(Published {})
    }
}

struct Published {}

impl State for Published {
    fn request_review(self: Box<Self>) -> Box<dyn State> {
        self
    }

    fn approve(self: Box<Self>) -> Box<dyn State> {
        self
    }

    fn content<'a>(&self, post: &'a Post) -> &'a str {
        &post.content
    }
}
```

## Encoding States and Behavior as Types
By implementing the state Design pattern in Rust as we'd have done in traditional object oriented programming language, we are not taking the full advantage of Rust. <mark class="y">We'd want to implement the library such that invalid states and transition are compile time error.</mark>

Instead of encapsulating various states as different struct, hiding away the implementation, we'll encode different states as different types.

Let's rewrite `lib.rs`:

```rust
pub struct Post {
    content: String,
}

pub struct DraftPost {
    content: String,
}
```

and then add `impl` block for both:

```rust
impl Post {
    pub fn new() -> DraftPost {
        DraftPost {
            content: String::new(),
        }
    }

    pub fn content(&self) -> &str {
        &self.content
    }
}

impl DraftPost {
    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text);
    }
}
```

<mark class="g">Our structs don't need `state` field anymore because we're moving the encoding of state to the type of struct.</mark>

The `DraftPost` struct also don't have content method, disabling any draft post to return their private `content`.

Also only way to create a `DraftPost` is to call `new()` function of `Post` struct and no way to create an instance of `Post` struct.

Next, we want ability to review a post, so we'll add `PendingReviewPost`:

**Notice we use `self` and not `&self`.**

```rust
pub struct PendingReviewPost {
    content: String,
}

impl PendingReviewPost {
    pub fn approve(self) -> Post {
        Post {
            content: self.content,
        }
    }
}
```

Only `PendingReviewPost` will have `approve()` method, returning a `Post` instance.

To get to pending review state, we'll add in a method on `DraftPost` to request for review:

```rust
impl DraftPost {
    // ...

    pub fn request_review(self) -> PendingReviewPost {
        PendingReviewPost {
            content: self.content
        }
    }
}
```

`request_review()` is going to return a `PendingReviewPost`. `request_review()` and `approve()` take ownership of `self`,  meaning they'll consume and invalidate the old state and return a new state.

Also, now only way to get `PendingReviewPost` is to `request_review()` on `DraftPost`.  We've now encoded the workflow into type system.

Our final `lib.rs` should look like:

```rust
// lib.rs
pub struct Post {
    content: String,
}

pub struct DraftPost {
    content: String,
}

impl Post {
    pub fn new() -> DraftPost {
        DraftPost {
            content: String::new(),
        }
    }

    pub fn content(&self) -> &str {
        &self.content
    }
}

impl DraftPost {
    pub fn add_text(&mut self, text: &str) {
        self.content.push_str(text);
    }

    pub fn request_review(self) -> PendingReviewPost {
        PendingReviewPost {
            content: self.content
        }
    }
}

pub struct PendingReviewPost {
    content: String,
}

impl PendingReviewPost {
    pub fn approve(self) -> Post {
        Post {
            content: self.content,
        }
    }
}
```

Latly, let's update `main.rs`:

- get rid of `post.content()` since this method cannot be called unless the method is published.
- `request_review()` and `approve()` no longer change the internal state, instead they return a new post type.

```rust
// main.rs
use blog::Post;

fn main() {
    let mut post = Post::new();

    post.add_text("I ate a salad for lunch today");

    let post = post.request_review();

    let post = post.approve();  // the regular `Post` instance has `content()` method
    assert_eq!("I ate a salad for lunch today", post.content());
}
```

Now invalid states are impossible to be represent using the type system.

Using Object Oriented patterns won't always be the best approach because of features such as Ownership in Rust that traditional Object Oriented programming languages don't have.
