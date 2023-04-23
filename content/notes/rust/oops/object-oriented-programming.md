# Object Oriented Programming in Rust

Object Oriented Programming in the context of Rust. Rust is inspired by many different programming languages, some Object oriented other functional.

For most Object Oriented Programming languages out there, three things are prominent:

1. Objects
2. Encapsulation
3. Inheritance

So, lets revise them and learn if they are supported in Rust?

[Object-Oriented Programming Features of Rust](https://doc.rust-lang.org/stable/book/ch17-00-oop.html){ .md-button }

## Objects
<mark class="v">Objects are made out of data and methods that operate on that data.</mark>

In the context of Rust, Structs and Enums are responsible for holding the data and we use `impl` block for implementing methods for those type defined by either `struct` or `enum`.

So, yes we get about the same functionality.

## Encapsulation
<mark class="v">Implementation details of an object are hidden from the code using that object.</mark>

The objects interaction with outside code is limited by the methods/APIs it provide allowing programmer to change the internals of an object without changinging the code which uses that object.

In Rust, we use `pub` keyword to decide which module, types, function, method are going to be public. Since otherwise everything is private by default.

```rust
pub struct AveragedCollection {
    list: Vec<i32>,
    average: f64,
}
```

The struct `AveragedCollection` is public, i.e., anyone outside the library can use it but it's fields are private. This struct is going to be used to serve as a cache. We want when the `list` is updated the `average` gets updated as well. If some outside code is allowed to manipulate `list`, it might not update `average` leaving inconsistent data. We want to provide this functionality via methods.

So something like this is necessary:

```rust
impl AveragedCollection {
    pub fn add(&mut self, value: i32) {
        self.list.push(value);
        self.update_average();
    }

    pub fn remove(&mut self) -> Option<i32> {
        let result = self.list.pop();
        match result {
            Some(value) => {
                self.update_average();
                Some(value)
            }
            None => None,
        }
    }

    pub fn average(&self) -> f64 {
        self.average
    }

    // a private method by default
    fn update_average(&self) {
         let total: i32 = self.list.iter().sum();
         self.average = total as f64 / self.list.len() as f64;
    }
}
```

## Inheritance
<mark class="v">Inheritance is the ability for an object to inherit from another object's definition gaining the data and behavior of that other object without having to define the data and behavior itself.</mark>

<mark class="r">**Rust doesn't support this feature of Object Oriented programming**.</mark> So, we can't define structs/enums that derive it's fields and methods from other struct/enum.

However, we do have other methods to accomplish something like that, depending on **why do we want Inheritance?**.

There are two main uses of Inheritance:

1. **Code sharing**: In Rust, we can use <mark class="b">default trait method implementation</mark>, so that all types and hence object can get the same behvior/methods (not fields) for which they use the same trait.
2. **Polymorphism**: <mark class="v">Polymorphism allows us to substitute multiple objects objects for each other at runtime for each other at runtime if they share certain characteristics.</mark> In traditional programming language, this is done via Parent class (say Vehicle) and child class (Scooter, truct, car) and at runtime for functions accepting Parent class, we can pass in child class.

    Rust uses different approach. <mark class="b">You can use generics to abstract away concrete type and use trait bounds to restrict the characteristics of those types.</mark>

    [Trait Bounds](/notes/rust/traits/#trait-bounds){ .md-button }

    In addition to that Rust also provides <mark class="b">Trait objects</mark> similar to generics except they use dynamic dispatch whereas generics use static dispatch.
