---
title: "Concurrency in Rust - Creating Threads"
description: ""
lead: ""
date: 2022-09-20T07:58:19+01:00
lastmod: 2022-09-20T07:58:19+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 23
toc: true
---

{{< alert >}}
Concurrent programming is when different parts of your program <mark class="v">execute independently.</mark> 

Parallel programming is when different parts of your program <mark class="v">execute at the same time.</mark>
{{< /alert >}}

Because of Rust's type system and powerful ownership model, we can write concurrent programs with lots of errors being caught at compile time. Meaning we can write code that is free of subtle bugs and easy to refactor, thus we call it *fearless concurrency*.

## Using Threads
An executed program's code is ran within a process and the operating system manages multiple processes at once.

Withing a program we can have independent parts that run simultaneously, ran by **threads**. This can improve the performance of our program since, multiple parts are running at the same time at the cost of complexity.

Since with concurrency, we don't have control over which part run at which time, we can few problems., such as **race conditions**, <mark class="y">where threads will try to access data/resource in inconsistent order.</mark>

Another such problem is **Deadlocks** where we can have two threads that are both waiting for a resource that the other thread has thus making both threads wait indefinitely.

{{< figure src="https://upload.wikimedia.org/wikipedia/commons/2/28/Process_deadlock.svg" caption="Source: [Wikipedia](https://en.wikipedia.org/wiki/Deadlock)" >}}

Also, because execution order is non-deterministic bugs can appear that can only happen in certain situation, hard to be caught during testing.

There are two main types of threads:

- **One-to-One threads** or **OS threads**: means that when we create a thread in our program it maps to an operating system thread
- **M-to-n threads** or **Program threads**: many programming language provide their own implementation of threads, these threads are not mapped to OS threads., i.e., we can many program threads being mapped to fewer OS threads. That's why it's called M-to-n model because we have "m" program threads that maps to "n" OS threads. 

Each model has its own advantages and disadvantages. The most important trade-off for Rust is runtime support, the code that is included by the programming language in every single binary. Rust aims to have extremely small runtime in fact almost no runtime at all, trading-off out-of-the-box features, the more feature we include out of the box, the larger the runtime will be. 

Since *program threads* will require larger runtime, Rust only include *OS threads* in its standard library. For *M-to-n threads* crates providing such functionalities are there.

## Creating a New Thread with spawn

```rust
use std::{thread, time::Duration};

fn main() {
    // call `spawn()` function and pass in closure
    thread::spawn(|| {
        // loop through 1..10 
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            // just pause execution of this thread
            thread::sleep(Duration::from_millis(1)); 
        }
    });

    // looping in main through 1..5 
    for i in 1..5 {
        println!("hi number {} from main thread!", i);
        thread::sleep(Duration::from_millis(1)); 
    }
}
```

Output might look different if you ran it, since the order is non-deterministic.

```text
hi number 1 from main thread!
hi number 1 from the spawned thread!
hi number 2 from main thread!
hi number 2 from the spawned thread!
hi number 3 from the spawned thread!
hi number 3 from main thread!
hi number 4 from the spawned thread!
hi number 4 from main thread!
hi number 5 from the spawned thread!
```

The main thread finished printing all of its numbers from 1 to 4 (since the range was exclusive) <mark class="y"> but the spawn thread didn't finish printing all of its number from 1 to 10.</mark> This is because, <mark class="v">**when main thread ends, the spawn thread is stopped no matter if it finished executing or not.** </mark>

Let's modify the code to let spawned thread to finish its execution.

## Using join handles.

1. Store the return type returned by `thread::spawn()` which is a `JoinHandle<T>` object.
2. Call `JoinHandle<T>.join()` method to wait for the spawned thread to finish.

```rust
use std::{thread, time::Duration};
 
fn main() {
    // call `spawn()` function and pass in closure
    let handle = thread::spawn(|| {
        // loop through 1..10 
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            // just pause execution of this thread
            thread::sleep(Duration::from_millis(1)); 
        }
    });
 
    // looping in main through 1..5 
    for i in 1..5 {
        println!("hi number {} from main thread!", i);
        thread::sleep(Duration::from_millis(1)); 
    }

    // call `unwrap()` because `join()` returns a `Result<T>`
    handle.join().unwrap();
}
```

Calling `join()` will block (stop from doing any further work/exit entirely) the thread currently running (which in this is main thread) until the thread associated with the handle (the spawn thread).

Running this updated code outputs, what we expect:

```text
hi number 1 from main thread!
hi number 1 from the spawned thread!
hi number 2 from main thread!
hi number 2 from the spawned thread!
hi number 3 from main thread!
hi number 3 from the spawned thread!
hi number 4 from main thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
hi number 6 from the spawned thread!
hi number 7 from the spawned thread!
hi number 8 from the spawned thread!
hi number 9 from the spawned thread!
```

If we move our call to `join()` method right after spawning the thread, like this:

```rust
use std::{thread, time::Duration};
 
fn main() {
    // call `spawn()` function and pass in closure
    let handle = thread::spawn(|| {
        // loop through 1..10 
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            // just pause execution of this thread
            thread::sleep(Duration::from_millis(1)); 
        }
    });

    handle.join().unwrap();

    // ...
```

Produces:

```text
hi number 1 from the spawned thread!
hi number 2 from the spawned thread!
hi number 3 from the spawned thread!
hi number 4 from the spawned thread!
hi number 5 from the spawned thread!
hi number 6 from the spawned thread!
hi number 7 from the spawned thread!
hi number 8 from the spawned thread!
hi number 9 from the spawned thread!
hi number 1 from main thread!
hi number 2 from main thread!
hi number 3 from main thread!
hi number 4 from main thread!
```

This is because the main thread kept waiting because we called `join()` right after spawning a new thread.

## Using move Closures with Threads
Up until now the thread didn't upon any variables outside of the thread. Things become wierd when variables are shared among variables. 

Here, in this code we just want to print out `v` from inside of a spawned thread. But this gives error:

```rust
use std::thread;

fn main() {
    let v = vec![1, 2, 3];

    let handle = thread::spawn(|| {
        //                     ^^ closure may outlive the current function, 
        // but it borrow `v`, which is owned by the current function.
        println!("Here's a vector: {:?}", v);
    });

    handle.join().unwrap();
}
```

Rust is trying to capture environment variables, and think we only need reference to `v` since we are printing `v`. <mark class="r">But that's a problem because Rust doesn't know how long the spawn thread will run for so it doesn't know if `v` will always be a valid reference or not.</mark>

Say, what if we dropped the variables after spawning the thread. This could lead to unintentional behavior. So we aren't allowed to have a reference of the variables passed to spawned threads.

```rust
//...
let handle = thread::spawn(|| {
    println!("Here's a vector: {:?}", v);
});
drop(v);

//...
```

Instead we need to take ownership using the `move` keyword. <mark class="v">`move` keyword tell Rust to not infer the values that closure as borrowed instead we want explicitly to move values inside the closure/ closure to take ownership.</mark> After this we'll not be able to call `v` in main thread.

```rust
    // ...
    let handle = thread::spawn(move || {
        println!("Here's a vector: {:?}", v);
    });

    handle.join().unwrap();
}
```


