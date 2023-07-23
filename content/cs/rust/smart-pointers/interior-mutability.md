# Smart Pointers in Rust - Interior Mutability

!!! info

    Interior mutability is a design pattern in Rust that allows you to mutate data in Rust even when there are immutable references to that data, typically disallowd by the borrowing rules.

    This pattern uses unsafe code inside a data structure to bypass the typical rules around mutation and borrowing. The unsafe code is wrapped around `unsafe` block and is not checked by borrow cheker at compile time for memory safety.

    **Although the borrow rules are not enforced at compile time, we may enforce it at run time**.

["RefCell<T> and the Interior Mutability Pattern](https://doc.rust-lang.org/stable/book/ch15-05-interior-mutability.html){ .md-button }

## Enforcing Borrowing Rules at Runtime
[Refcell](https://doc.rust-lang.org/std/cell/struct.RefCell.html) smart pointer represents single ownership over the data it holds kind of like `Box` smart pointer. The difference being the `Box` smart pointer enforces borrowing rules at compile time wheread `RefCell` enforces these rules at run time.

**This means if we break the borrowing rules at run time, the program will panic at exit.**

Compile time borrow checks means we can catch error sooner in the development cycle with no runtime performance cost.

<mark class="y">The advantage of checking borrowing rules at runtime is that certain memory safe scenarios are allowed whereas they would be disallowed at compile time.</mark>

This is because certain properties of a program are impossible to detect using static analysis. The most famous example of this is the Halting problem:

<iframe width="999" height="400" src="https://www.youtube.com/embed/t37GQgUPa6k" title="The Halting Problem - An Impossible Problem to Solve" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<mark class="v">`RefCell` smart pointer is useful when you're sure that your code is following the borrowing rules but the compiler can't understand or gurantee that.</mark> **You can only use `RefCell` smart pointer is single threaded programs.

Here is a recap of the reasons to choose `Box<T>`, `Rc<T>`, or `RefCell<T>`:
- `Rc<T>` enables multiple owners of the same data; `Box<T>` and `RefCell<T>` have single owners.
- `Box<T>` allows immutable and mutable borrows checked at compile time; `Rc<T>` allows only immutable borrows checked at compile time; `RefCell<T>` allows immutable and mutable borrows checked at runtime.
- Because `RefCell<T>` allows mutable borrows checked at runtime, you can mutate the value inside the `RefCell<T>` even when the `RefCell<T>` is immutable. `Box<T>` doesn't allows that, it would require `Box<T>` to mutable as well.

<mark class="v">**Mutating the value inside an immutable value is the _interior mutability pattern_**.</mark>

## Interior Mutability Pattern
The borrowing rules checked at compile time doesn't allow us to mutate a value using an immutable reference to a mutable data.

```rust
fn main() {
    let a = 5;
    let b = &mut a; // mutable borrow to `a`
    //      ^^^^^^ error: cannot borrow `a` as mutable, as it is not declared mutable
    let mut c = 10;
    let d = &c;     // immutable borrow to `c`
    *d = 20;
//  ^^^^^^^^ error: cannot assign to `*` which is behind a `&` reference `d` is a `&`
//                  reference, so the data it refers to cannot be written
}
```

Though we could solve this with some indirection. Let's say we have a data structure that stores some value and inside that data structure the value is mutable *but* when we get reference to that data structure the **reference itself is immutable**. Code outside of the data structure would not be able to mutate the data but it's methods can.

`RefCell` does exactly that, using which we can call methods to get an immutable or mutable reference to the data.

## Interior Mutability: Mock Objects
Let's take an example where we're trying to build a library that tracks a value against a maximum value and sends messages depending on how close the value is to the maximum value. This can be useful in scenario where we want to trak how much API calls a user is able to make.

This library will only provide the functionality to track how close the value is to maximum and what messages is to send at what time. The application depending on this library will be going to implement how the message is actually supposed to be send.

```rust
pub trait Messenger {
    fn send(&self, msg: &str);
}

pub struct LimitTracker<'a, T: Messenger> {
    // Since we're borrowing `T` we must use lifetimes
    messenger: &'a T,   // a referece to generic type T that must implement `Messenger`
    // usize is a pointer-sized unsigned integer type
    // adapts to u32 or u64, depending on the architecture of the computer (32/64 bits)
    value: usize,
    max: usize
}

impl<'a, T> LimitTracker<'a, T>
where
    T: Messenger,
{
    pub fn new(messenger: &T, max: usize) -> LimitTracker<T> {
        LimitTracker {
            messenger,
            value: 0,
            max
        }
    }

    pub fn set_value(&mut self, value: usize) {
        self.value = value;

        let percentage_of_max = self.value as f64 / self.max as f64;

        if percentage_of_max >= 1.0 {
            self.messenger.send("Error: You are over your quota!")
        } else if percentage_of_max >= 0.9 {
            self.messenger
                .send("Urgent warning: You'ver used up over 90% of your quota!");
        } else if percentage_of_max >= 0.75 {
            self.messenger
                .send("Warning: You've used up over 75% of your quota!");
        }
    }
}
```

Say we want to test our library at certain points, like 75%, 90% and 100% as quota runs out. We could test this code using a **mock object**.

When we send a message we call `self.messenger.send()`. So imagine if we pass in a mock messenger object to our limit tracker struct. Our mock messenger object could keep track of how many times the send method was called.

Let's implement the test:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    struct MockMessenger {
        sent_messages: Vec<String>,
    }

    impl MockMessenger {
        fn new() -> MockMessenger {
            MockMessenger {
                sent_messages: vec![],
            }
        }
    }

    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            // instead of sending messages; just push into the `sent_messages` vector
            self.sent_messages.push(String::from(message));
        //  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        //  error: cannot borrow `self.sent_messages` as mutable, as it is behind a `&` reference
        //  `self` is a `&` reference, so the data it refers to cannot be borrowed as mutable
        }
    }

    #[test]
    fn it_sends_an_over_75_percent_warning_message() {
        let mock_messenger = MockMessenger::new();
        let mut limit_tracker = LimitTracker::new(&mock_messenger, 100);

        limit_tracker.set_value(80);

        assert_eq!(mock_messenger.sent_messages.len(), 1);
    }
}
```

The error above indicates that we are using an immutable reference of `self` which is an instance `MockMessenger` that means inside that struct any field inside that struct should be immutable as well. But we cannot make `&self` mutable , i.e., `&mut self` since the trait defines the *function signature* requires a immutable reference.

What we need here is *Interior Mutability*.

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    struct MockMessenger {
        sent_messages: RefCell<Vec<String>>,
    }

    impl MockMessenger {
        fn new() -> MockMessenger {
            MockMessenger {
                // wrap the empty vector in `RefCell`
                sent_messages: RefCell::new(vec![]),
            }
        }
    }

    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            // call `borrow_mut()` on `RefCell` smart pointer
            self.sent_messages.borrow_mut().push(String::from(message));
        }
    }

    #[test]
    fn it_sends_an_over_75_percent_warning_message() {
        let mock_messenger = MockMessenger::new();
        let mut limit_tracker = LimitTracker::new(&mock_messenger, 100);

        limit_tracker.set_value(80);

        // call `borrow()` to get an immutable reference to struct field
        assert_eq!(mock_messenger.sent_messages.borrow().len(), 1);
    }
}
```
The tests passes in this case.


## Borrowing Rules with RefCell
We know that `RefCell` check borrow rules at runtime, we cannot have two mutable reference for a value at same time. Let's see what happens incase we do have:

```rust
mod tests {
    // ...

    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            let mut one_borrow = self.sent_messages.borrow_mut();
            let mut two_borrow = self.sent_messages.borrow_mut();

            one_borrow.push(String::from(message));
            two_borrow.push(String::from(message));
        }
    }

    // ...
}
```

If we run `cargo test` for this update test, it fails:

```text
running 1 test
test tests::it_sends_an_over_75_percent_warning_message ... FAILED

failures:

---- tests::it_sends_an_over_75_percent_warning_message stdout ----
thread 'tests::it_sends_an_over_75_percent_warning_message' panicked at 'already borrowed: BorrowMutError', src/lib.rs:64:53
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace


failures:
    tests::it_sends_an_over_75_percent_warning_message

test result: FAILED. 0 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

Also note that since we are checking borrowing rules at runtime, this does cost a small overhead on runtime performace of the program.

## Combining Rc and RefCell
Combining them we want <mark class="v">to achieve multiple owners of mutable data</mark>. In our original `Cons` list we used `Rc` to create two list that shared a Third list. But the values inside them were immutable.

Now, with `RefCell` we can make them mutable.

```rust
#[derive(Debug)]
enum List {
    // wrapped inside Rc to have multiple owners.
    // i32 is wrapped inside `RefCell` to make it mutable
    Cons(Rc<RefCell<i32>>, Rc<List>),
    Nil,
}

use crate::List::{Cons, Nil};
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    let value = Rc::new(RefCell::new(5));

    let a = Rc::new(Cons(Rc::clone(&value), Rc::new(Nil)));

    let b = Cons(Rc::new(RefCell::new(3)), Rc::clone(&a));
    let c = Cons(Rc::new(RefCell::new(4)), Rc::clone(&a));

    *value.borrow_mut() += 10;

    println!("a after = {:?}", a);
    println!("b after = {:?}", b);
    println!("c after = {:?}", c);
}
```

Running this, the update done once appears in all three list:

```text
a after = Cons(RefCell { value: 15 }, Nil)
b after = Cons(RefCell { value: 3 }, Cons(RefCell { value: 15 }, Nil))
c after = Cons(RefCell { value: 4 }, Cons(RefCell { value: 15 }, Nil))
```
