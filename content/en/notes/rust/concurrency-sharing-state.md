---
title: "Concurrency in Rust - Sharing State"
description: ""
lead: ""
date: 2022-09-20T07:58:21+01:00
lastmod: 2022-09-20T07:58:21+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 25
toc: true
---

Message passing a one way to pass data between concurrent threads. Other way to do is usin Sharing state.

Transferring data using shared state concurrency we have some piece of data that multiple threads can read and write to.

{{< link title="Shared-State Concurrency" link="https://doc.rust-lang.org/stable/book/ch16-03-shared-state.html" >}}

## The API of Mutex

{{< alert title="What are mutexes?" >}}
Mutex is an abbreviation for **Mutual Exclusion**.

That means for a piece of data only one thread can have access to the data at a given time.
{{< /alert >}}

To achieve the mutexes use locking system. When a thread wants access to a piece of data behind a mutex, it will signal that it wants access to the data and acquire the mutexe's lock.

<mark class="v">The lock is a data structure that keeps track of which thread has exclusive access to a piece of data.</mark>

Lock disallow access to that piece of data to any another thread. Once the thread is done with the data, it can unlock the piece of data and let other threads to get lock of it/access it.

Mutex are known for being hard to use due to:

1. We need to acquire the lock before we access the data.
2. We have to release the lock when we are done with the data so that other threads can access.

But don't worry, Rust got you covered so that you don't get the locking/unlocking wrong.

```rust
use std::sync::Mutex;

fn main() {
    // to create a new Mutex
    let m = Mutex::new(5);

    // let's access the data in Mutex
    {
        // call `lock()` to acquire lock
        // block current thread until that lock is able to be acquired
        let mut num = m.lock().unwrap();
        *num = 6;      // mutate the value
    }

    println!("m = {:?}", m);
}
```

Calling `lock()` this returns an `Option<T>` because if there is already a thread that has a lock to that data and that thread panics, then calling `lock()` will fail. Calling `unwrap()` will return a `MutexGuard<T>` smart pointer whose `Deref` trait points to inner data of the Mutex. `MutexGuard<T>` implements `Drop` trait such that when it goes out of scope, it releases lock to the data.

Running this produces:

```text
m = Mutex { data: 6, poisoned: false, .. }
```

## Sharing Mutex between Multiple Threads
We'll create a new mutex that holds the integer value and we'll spin up 10 threads, each incrementing the value to reach the result of 10.

```rust
use std::sync::Mutex;
use std::thread;

fn main() {
    let counter = Mutex::new(0);
    let mut handles = vec![];

    // create threads
    for _ in 0..10 {
        let handle = thread::spawn(move || {
            //                     ^^^^ use of moved value: `counter`
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handels.push(handle);
    }

    for handle in hanldes {
        handle.join().unwrap();
    }

    println!("Result: {}", *counter.lock().unwrap());
}
```

But we have an error. `counter` was already moved in the previous iteration to the first thread we created.

## Multiple Ownership with Multiple Threads
We want to allow counter to have multiple owners and this can be made possible with `Rc<T>` smart pointer. 

So, let's update the code:

```rust
use std::sync::Mutex;
use std::thread;
use std::rc::Rc;
 
fn main() {
    let counter = Rc::new(Mutex::new(0)); // wrap mutex in `Rc`
    let mut handles = vec![];
 
    // create threads
    for _ in 0..10 {
        // a counter that shadows original counter
        let counter = Rc::clone(&counter);

        let handle = thread::spawn(move || {
            //       ^^^^^^^^^^^^^ error: `Rc<Mutex<i32>>` cannot be sent between threads safely
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }
 
    for handle in handles {
        handle.join().unwrap();
    }
 
    println!("Result: {}", *counter.lock().unwrap());
}
```

But this creates new error.<mark class="r"> `Rc<T>` gives us the functionality we want, but it's not thread safe.</mark> 

For our use case we want Atomic Reference counting smart pointer. Atomics are like primitive types except they can be shared among threads.

```rust
use std::sync::{Arc, Mutex};
use std::thread;
 
fn main() {
    let counter = Arc::new(Mutex::new(0)); // wrap mutex in `Rc`
    let mut handles = vec![];
 
    // create threads
    for _ in 0..10 {
        // a counter that shadows original counter
        let counter = Arc::clone(&counter);

        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }
 
    for handle in hanldes {
        handle.join().unwrap();
    }
 
    println!("Result: {}", *counter.lock().unwrap());
}
```

Running this produces:

```text
Result: 10
```

Even though counter is immutable but we could mutate the inner value via a mutable reference, that's because `Mutex<T>` uses interior mutability.

## RefCell/Rc and Mutex/Arc
{{< alert type="success" >}}
In the same way that the `RefCell<T>` allows us to mutate value inside `Rc<T>`; `Mutex<T>` allows us to mutate value inside `Arc<T>` smart pointer. 

`RefCell<T>` comes with the risk of creating circular dependencies & `Mutex<T>` comes with the risk of creating deadlocks.
{{< /alert >}}

