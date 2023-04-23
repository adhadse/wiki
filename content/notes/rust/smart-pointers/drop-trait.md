# Smart Pointers in Rust - The Drop Trait

The `Drop` trait can be implemeted on any type and allows us to customize when a value goes out of scope.

In some languages, we have to manually deallocate the data stored on the heap when we're done using the smart pointer, but with `Drop` trait this clean up happens automatically when a value goes out of scope.

[Running Code on Cleanup with the Drop Trait](https://doc.rust-lang.org/stable/book/ch15-03-drop.html){ .md-button }

```rust
struct CustomSmartPointer {
    data: String
}

// the drop trait is already included in prelude; already in scope
impl Drop for CustomSmartPointer {
    fn drop(&mut self) {
        println!("Dropping CustomSmartPointer with data `{}`!", self.data);
    }
}

fn main() {
    let c = CustomSmartPointer {
        data: String::from("my stuff"),
    };

    let d = CustomSmartPointer {
        data: String::from("other stuff"),
    };

    println!("CustomSmartPointers created.");

    // variables will be dropped in reverse order of their creation
    // first d then c
}
```

Running this produces:

```text
CustomSmartPointers created.
Dropping CustomSmartPointer with data `other stuff`!
Dropping CustomSmartPointer with data `my stuff`!
```

In most cases customizing this cleanup behavior isn't necessary per say, but in some cases to cleanup value early such as when using smart pointers to manage locks.

<mark class="y">We might want to call the drop method to release a lock so other code in the same scope</mark>

!!! info

    It's worth noting that the `drop()` in std is just the empty function. It simply takes ownership of the value and make it go out of scope.

## Drop method with std::mem::drop
Rust doesn't allows us to call the drop method directly. For example something like:

```rust
fn main() {
    let c = CustomSmartPointer {
        data: String::from("some data"),
    };
    println!("CustomSmartPointer created.");
    c.drop();
    println!("CustomSmartPointer dropped before the end of main.");
}
```

when calling `cargo check` from terminal:

```text
error[E0040]: explicit use of destructor method
  --> src/main.rs:17:7
   |
17 |     c.drop();
   |     --^^^^--
   |     | |
   |     | explicit destructor calls not allowed
   |     help: consider using `drop` function: `drop(c)`
```

Rust doesn't allow us to call the drop method manually because when our variable goes out of scope, Rust will still automatically call the drop method.

<mark class="v">In other to clean up a value early, we can call the drop fucntion provided by Rust standard library and passing the value</mark>

```rust
// c.drop();
drop(c);
```
