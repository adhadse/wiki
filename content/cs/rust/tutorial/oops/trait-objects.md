# Using Trait Objects in Rust
Although Rust doesn't support classical inheritance, it does support polymorphism through generics and Trait Objects.

[Using Trait Objects That Allow for Values of Different Types](https://doc.rust-lang.org/stable/book/ch17-02-trait-objects.html){ .md-button }

## Trait for Common Behavior
Imagine we're building a GUI library to take a list of visual components (buttons, checkbox, etc) and draw them to screen. In addition to that we'd like our users to extend that library, i.e., they could create their own visual components and draw them on screen.

All these visual components are going to have a method called `draw()`.

In traditional programming concepts, we're going to have a base class like `VisualComponent` having a `draw()` method, other visual component will inherit from this class. They'll also be able to override the `draw()` method with their own implementation.

In Rust, we define shared behavior using traits, so let's write a trait `draw` with a method `draw()`:

We'll create a new project with structure like this, having `main.rs` and `lib.rs`:

```text
.
├── Cargo.toml
├── .gitignore
└── src
    ├── lib.rs
    └── main.rs
```

In our `lib.rs`:

```rust
// lib.rs
pub trait Draw {
    fn draw(&self);
}

pub struct Screen {
    pub components: Vec<Box<dyn Draw>>,
}
```

Here, <mark class="y">`components` is vector of *trait object*</mark>.

We define a trait object by first specifying some sort of pointer such as a reference or a `Box<T>` smart pointer then using `dyn` keyword followed by the trait name. `dyn` stands for dynamic dispatch.

Why trait object need to use some sort of pointer? Here is the answer:

[Dynamically sized types](/cs/rust/advanced/advanced-types/#traits-and-dynamically-sized-types){ .md-button }

<mark class="v">Now, Rust will ensure at compile time that any object in this vector implements the `Draw` trait.</mark>

Let's create another `impl` block for `Screen` that implements `run()` that iterate through components and run them.

```rust
// lib.rs
// in continuation ...
impl Screen {
    pub fn run(&self) {
        // `iter()` let's us iterate without taking ownership
        for component in self.components.iter() {
            component.draw()
        }
    }
}
```

So, now a component is anything that implements `Draw` trait. These component can then be iterated and by calling their `run()` method will be drawn to the screen.

But why not generics?

Let's talk about that,

```rust
pub struct Screen<T: Draw> {  // a trait bound
    pub components: Vec<T>,   // vec will store anything of type T
}

impl<T> Screen<T>
where
    T: Draw,
{
    pub fn run(&self) {
        for component in self.components.iter() {
            component.draw();
        }
    }
}
```

So, isn't this the same functionality as our trait object implementation?

But there is one main difference here.

Our list `components` can only store a list of one type of component that implements `Draw` trait. So the list is homogeneous.

```rust
let components: Vec<Slider>;
let components: Vec<CheckBox>;
let components: Vec<Button>;
```

<mark class="y">It won't be possible to store a mixture of different components.</mark> But using trait objects, do have a performance cost.

## Implementing the Trait
Let's implement some components:

```rust
// lib.rs
pub trait Draw {
    fn draw(&self);
}

pub struct Screen {
    pub components: Vec<Box<dyn Draw>>,
}

impl Screen {
    pub fn run(&self) {
        // `iter()` let's us iterate without taking ownership
        for component in self.components.iter() {
            component.draw()
        }
    }
}

// A component can implement different method other than
// what required by Trait such `on_click()` inside `impl Button {}`
pub struct Button {
    // these fields are relevant to `Button` component
    // another component might have different fields
    pub width: u32,
    pub height: u32,
    pub label: String,
}

impl Draw for Button {
    fn draw(&self) {
        // draw button
    }
}
```

And this is how consumers are going to define there own drawable components:

In `main.rs`:

```rust
use gui_lib::{Screen, Button, Draw};

// custom component
struct SelectBox {
    width: u32,
    height: u32,
    options: Vec<String>
}

impl Draw for SelectBox {
    fn draw(&self) {
        // draw select box
    }
}

fn main() {
    let screen = Screen {
        components: vec![
            Box::new(SelectBox {
                width: 100,
                height: 100,
                options: vec![
                    String::from("yes"),
                    String::from("no"),
                    String::from("maybe"),
                ]
            }),
            Box::new(Button {
                width: 100,
                height: 100,
                label: String::from("ok")
            })
        ]
    };

    screen.run();
}
```

Because we're using trait object Rust will ensure at compile time that every component in the list `components` implements the `Draw` trait.

If we add in an element that does not implement `Draw` trait, like so:

```rust
let screen = Screen {
        components: vec![
            Box::new(String::from("test")),
        // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        // error: the trait bound `String: Draw` is not satisfied required for the
        // cast to the object type `dyn Draw`.
            Box::new(SelectBox {
                width: 100,
                height: 100,
                options: vec![
                    String::from("yes"),
                    String::from("no"),
                    String::from("maybe"),
                ]
            }),
            //...
```

## Static vs Dynamic Dispatch

<mark class="v">Monomorphization is a process where the compiler will generate non-generic implementations of functions based on the concrete types used in place of generic types.</mark>

For eg., we have a generic function called `add()` which takes two generic parameters and adds them. To use that function with floating pointer numbers or integers, the compiler will generate `integer_add()` and then a `float_add()`, and then find all invocation of `add()` method and replace them concrete function for individual types.

So,<mark class="v"> we're taking a generic implementation and substituting it for concrete implementation. This is called as Static Dispatch.</mark>

<mark class="y">In dynamic dispatch, the compiler does not know the concrete methods you're calling at compile time so instead it figures that out at run time.</mark>

When using Trait object the Rust compiler must use Dynamic dispatch because the compiler doens't know all the concrete objects that are going to be used at compile time. The compiler will add code to figure out the correct method to call at runtime adding up performance cost.

## Object Safety for Trait Objects

**We can only make object safe traits into trait bounds.**

!!! info "To be object safe;"

    A trait is object safe when all of the methods implemented on that trait have these two properties:

    1. The return type is not `Self`.
    2. There are no generic parameters
