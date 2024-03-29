# Box Smart Pointer in Rust

To understand Box smart pointer, we'll need to revise our concept of pointers.

!!! info "What is pointer?"

    A pointer is a variable that stores the memory address that points to some other data in memory.

The most common pointer in Rust is a Reference. References simply borrows the value they point to without getting the ownership of the data. The simplicity means they don't have much overhead, unlike smart pointer which we are going to discuss.

!!! info "What are smart pointers?"

    Smart pointers are data structures that act like a pointer but have metadata and extra capabilities.

- In many cases the smart pointers own the data they point to.
- Strings and Vectors is one such example of smart pointer.
- The implementation involves structs combined with `Deref` and `Drop` traits.

<mark class="y">`Deref` trait allows instances of our smart pointer struct to be treated like references.</mark>

<mark class="y">`Drop` trait allows us to customize the code that is run when an instance of your smart pointer goes out of scope.</mark>

In this section, we'll covering most commonly seen smart pointers in Rust. Many third-party libraries implement their own custom smart pointers.

[Using Box<T> to Point to Data on the Heap](https://doc.rust-lang.org/stable/book/ch15-01-box.html){ .md-button }


## Using a Box to Store Data

!!! info "Box smart pointer"

    `Box` smart pointer allows us to store data on the Heap.
    They don't add much overhead except storing data on heap, but then you also don't provide you much capabilities.

    Useful when:

    - <mark class="v">When we have a type whose exact size cannot be known at compile time and we want to use a value of that type in a context which requires knowing the exact size.</mark>
    - When we have large amount of data and we want to transfer ownership without being copied.
    - When we own a value and we only care that the value implements a specific trait rather than it being a specific type(**trait object**).

The code below shows a simple example, but it isn't really viable. Storing the value on stack will make a lot more sense.
```rust
fn main() {
    // `b` stores the pointer on stack to that memory location on heap
    let b = Box::new(5); // store 5 on the heap
    println!("b = {}", b); // the boxed value can be used as if it was stored on stack
}
```

## Enabling Recursive Types with Boxes
Rust needs to know how much space a type takes up at compile type.

But in the given below example (and with recursive enums), we can recurse forever and we won't know how much space an enum can take.

Here we implement [Cons List](https://en.wikipedia.org/wiki/Cons) that comes from Lisp Programming language.

```rust
// A recursive enum with two variants
enum List {
    Cons(i32, List),
    Nil,
}

use List::{Cons, Nil};

fn main() {
    // A Con cell that stores 1, then a Con cell that stores 2
    // and finally another cell that stores 3 and at last Nil
    let list = Cons(1, Cons(2, Cons(3, Nil)));
}
```

This fails with error:

```text
error[E0072]: recursive type `List` has infinite size
 --> src/main.rs:2:1
  |
2 | enum List {
  | ^^^^^^^^^ recursive type has infinite size
3 |     Cons(i32, List),
  |               ---- recursive without indirection
  |
help: insert some indirection (e.g., a `Box`, `Rc`, or `&`) to make `List` representable
  |
3 |     Cons(i32, Box<List>),
  |               ++++    +
```

!!! info "How Rust computes the size of non-recursive enums"

    It's going to go through each variant and see how much size a variant needs.

    So for example,
    ```rust
    enum Message {
        Quit,                       // no space required
        Move { x: i32, y: i32 },    // 2-integers
        Write(String),              // a string
        ChangeColor(i32, i32, i32)  // 3-integers
    }
    ```

    Since the `enum` can take the maximum space that a variant with maximum space required is gonna use. The same can be said for the `List` enum we defined above.

    ```rust
    enum List {
        Cons(i32, List),  // this does require some space. But that's recursive! What is exact space required?
        Nil,              // no spae required
    }
    ```

To fix this wrap the `List` inside a `Box` smart pointer:

```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}
```

Let's try to determine the size of `List` again:

```rust
enum List {
    Cons(i32, Box<List>), // fixed space, an integer and a Box pointer pointing to memory in Heap
    Nil,             // no space required
}
```

**So now with the help of `Box` smart pointer, the `List` instead of being stored on stack, is getting stored on Heap memory. On stack only a pointer of fixed size takes into account the size of our enum `List`**

To finish it up:

```rust
// This compiles successfully ✅
enum List {
    Cons(i32, Box<List>),
    Nil
}

use List::{Cons, Nil};

fn main() {
    let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));
}
```
