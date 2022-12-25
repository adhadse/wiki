---
title: "Concurrency in Rust - Message Passing"
description: ""
lead: ""
date: 2022-09-20T07:58:20+01:00
lastmod: 2022-09-20T07:58:20+01:00
images: []
type: docs
draft: false
menu: 
  rust:
    parent: "concurrency"
weight: 2
toc: true
---

Message passing between threads is one very popular approach to safe concurrency. 

The Go programming language has a slogan that summarizeds this approach:

> Do not communicate by sharing memory instead share memory by communicating.

Rust provides **channels** via standard library to enable message passing. <mark class="y">A channel in programming has two halves, the transmitter and the receiver. </mark> 

<mark class="v">A transmitter is the upstream location where the message originates and at receiver it ends the message transmission.</mark>

One part of our code calls method on the transmitter passing in the data you want to send and another part of our is listening to the receiver for arriving messages. The channel is said to be closed if either the transmitter or the receiver half is dropped. 

{{< link title="Using Message Passing to Transfer Data Between Threads" link="https://doc.rust-lang.org/stable/book/ch16-02-message-passing.html" >}}

## Transfer Data Between Threads
We'll bring in `mpsc` module from the standard library into scope. `mpsc` stands for Multi-produce, single-consumer FIFO queue.

So, in Rust, we can have multiple producers of messages but only single receiver of messages.

```rust
use std::sync::mpsc;
use std::thread;
 
fn main() {
    // to create a channel call `channel()` method on `mpsc` module.
    // this returns a sender and receiver
    let (tx, rx) = mpsc::channel();
 
    // in order to sender to send message, we need to move `tx` into 
    // the closure
    thread::spawn(move || {
        let msg = String::from("hi");
        // unwrap because if receiving ends get dropped for some reason 
        // while sending message, `send()` will return an error
        // Right now we panic; but for production use case, handle it gracefully
        tx.send(msg).unwrap();
    });
 
    // the receiver end
    let received = rx.recv().unwrap();
    println!("Got: {}", received);
}
```

`rx<T>` also have `try_recv()` which doesn't block main thread execution instead it will return a result type immediately. `try_recv()` is useful when we want our thread to do other work, say, for example a loop to check with `try_recv()` for new message otherwise do other work.

Running this produces:

```text
Got: hi
```

## Channels and Ownership Transference
Ownership rules help us prevent errors in our concurrent code.

For example let's try to use `msg` after sending it down via channel:

```rust
use std::sync::mpsc;
use std::thread;
 
fn main() {
    let (tx, rx) = mpsc::channel();
 
    thread::spawn(move || {
        let msg = String::from("hi");
        tx.send(msg).unwrap();       // send takes ownership of value
        println!("msg is {}", msg);
        //                    ^^^ borrow of moved value: `msg`
        //                    value borrowed here after move 
    });
 
    let received = rx.recv().unwrap();
    println!("Got: {}", received);
}
```

This is problematic, since once we send the message via channel and could use it, in that case we could potentially modify or drop the variable.

## Sending multiple values
Let's modify the code to send multiple message to prove concurrency.

To do that, create a vector of values:

```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;
 
fn main() {
    let (tx, rx) = mpsc::channel();
 
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];

        // then loop through `val` and send each message
        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });
 
    // treat `rx` as an iterator;
    // every iteration will have a value passed into the channel
    // when channel closes iteration ends
    for received in rx {
        println!("Got: {}", received);
    }
}
```

Running this generates, with a second delay:

```text
Got: hi
Got: from
Got: the
Got: thread
```

## Creating multiple produces
Say, we have two threads that send messages.

```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;
 
fn main() {
    let (tx, rx) = mpsc::channel();

    // clone original `tx` sender
    let tx2 = tx.clone();
 
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];
 
        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    thread::spawn(move || {
        let vals = vec![
            String::from("move"),
            String::from("messages"),
            String::from("for"),
            String::from("you"),
        ];
 
        for val in vals {
            tx2.send(val).unwrap();   // `tx2` instead of `tx`
            thread::sleep(Duration::from_secs(1));
        }
    });
 
    // now we have two threads passing down messages down the channel
    for received in rx {
        println!("Got: {}", received);
    }
}
```

Running this produces a non-deterministic output, might differ for you each time:

```text
Got: hi
Got: move
Got: from
Got: messages
Got: for
Got: the
Got: you
Got: thread
```