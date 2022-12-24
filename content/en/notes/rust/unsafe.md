---
title: "Writing Unsafe Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:27+01:00
lastmod: 2022-09-20T07:58:27+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 31
toc: true
---

{{< link title="Unsafe Rust" link="https://doc.rust-lang.org/stable/book/ch19-01-unsafe-rust.html" >}}

## Unsafe Superpowers
Up until now the code we have wrote followed Rust memory safety guidelines and checked at compile time.

To opt out of these memory safety guarantees then we need to use unsafe Rust.

This exist for two reasons:

1. <mark class="y">Static Analysis is conservative by nature.</mark>

    Rust will reject a valid program if it can't guarantee that the program is memory safe even though you as a developer know it is.
2. <mark class="y">Underlying computer hardware is inherently unsafe.</mark>

    If Rust can't allow you to do certain unsafe operations then you couldn't do certain tasks. Since it is systems programming language so it must allow you to do low-level systems programming which sometimes require unsafe code.

Unsafe code is written in `unsafe` block and gives you five abilities: 

1. <mark class="y">Dereference a raw pointer</mark>
2. <mark class="y">Call an unsafe function or method</mark>
3. <mark class="y">Access or modify a mutable static variable</mark>
4. <mark class="y">Implement an unsafe trait</mark>
5. <mark class="y">Access fields of unions</mark>

Although unsafe doens't disable borrow checker or disable Rust safety checks. For e.g., if you have a reference inside `unsafe` it'll still be checked.

It's upto developer to make sure that memory inside `unsafe` is handled appropriately. Keep `unsafe` block small and manageable. We can also enclose unsafe code in a safe abstration and provide a safe API.

## Dereferncing a Raw Pointer
The compiler ensures references are valid. 

{{< ref title="Dandling References" link="/notes/rust/ownership.md" subsection="#dangling-references" >}}

Unsafe Rust has two types of raw pointers similar to references.   T
1. Immutable raw pointer (`*const <T>`)
    The pointer can't be directly assigned after it has been dereferenced.
2. Mutable raw pointer (`*mut <T>`)

The `*` here isn't dereference operator.

```rust
fn main() {
    let mut num = 5;

    let r1 = &num as *const i32;   // Immutable raw pointer
    let r2 = &mut num as *mut i32; // Mutable raw pointer
}
```
We don't use `unsafe` keyword here. That's because Rust allows us to create raw pointers but doesn't allow us to dereference them unless done in `unsafe` block.

The `as` keyword is used to cast a immutable reference and mutable reference to their corresponding raw pointer types.

Raw pointer are different from Smart pointers:
- Raw pointers are <mark class="r">allowed to ignore Rust borrowing rules</mark> by having mutable and immutable pointer or multiple mutable pointers to the same location in memory.
- Raw pointers are also <mark class="r">not guaranteed to point to valid memory.</mark>
- Raw pointer are <mark class="r">allowed to be null</mark>. 
- Raw pointer <mark class="r">don't implement any automatic cleanup.</mark>

We do know that the raw pointers we created above are valid, but that won't be true always incase of raw pointers. for e.g., let create a pointer to an arbitrary memory address:

```rust
fn main() {
    let address = 0x012345usize;
    let r3 = address as *const i32;
}
```

In this example there might be valid memory or there might not be at that `address`. This can lead to undefined behavior. Compiler might try to optimize the code such that there is no memory access or we may get segmentation fault.

Let's try to dereference our original `r1` & `r2` raw pointers by using `unsafe`:

```rust
fn main() {
    let mut num = 5;

    let r1 = &num as *const i32;   
    let r2 = &mut num as *mut i32; 

    unsafe {
        println!("r1 is: {}", *r1);
        println!("r2 is: {}", *r2);
    }
}
```

Running this works fine:

```text
r1 is: 5
r2 is: 5
```

If we were to create an immutable and mutable reference to the same location in memory then the program would not compile because that would violate ownership rules. Raw pointers allow us to bypass those rules but can lead to data races.

## Calling Unsafe Function or Method
Unsafe functions or methods look the same as regular functions or methods, except they have a `unsafe` keyword at the beginning of their definition.

`unsafe` in this context means that the function requires correct arguments otherwise it could lead to undefined behavior.

So do make sure to read documentation suggesting the requirements of unsafe function for upholding the functions contracts.

Unsafe functions must be called inside other `unsafe` functions or inside `unsafe` block.

```rust
fn main() {
    unsafe fn dangerous() {
        // no need for unsafe block inside unsafe function
    }

    unsafe {
        dangerous();
    }

    // unsafe {
        dangerous();
    //  ^^^^^^^^^^^ error: this operation is unsafe and requires an unsafe function or block    
    // }
}
```

## Creating a Safe Abstration
<mark class="y">Just because a function contains unsafe code doesn't make it an unsafe function.</mark>

You can wrap unsafe code inside a safe one.

```rust
fn main() {
    let mut v = vec![1, 2, 3, 4, 5, 6];

    let r = &mut v[..]; // create a mutable slice `r` of `v`

    let (a, b) = r.split_at_mut(3); // this will return tuple

    assert_eq!(a, &mut [1, 2, 3]);
    assert_eq!(b, &mut [4, 5, 6]);
}
```

`split_at_mut()` is a safe method implemented on mutable slices which will split the slice into two slices along the index passed in.

Imagine we wanted to split this function using only safe Rust code. Which might look something like this:

```rust
// for simplicity we implement function not a method
fn slit_at_mut(sliceL &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();

    assert_eq!(mid <= len);

    // return a tuple with two slices
    // first slice everything upto midpoint, second slice everything after midpoit
    (&mut slice[..mid], &mut slice[mid..])
    //    ^^^^^              ^^^^^ 
    // error: cannot borrow `*slice` as mutable more than once a time
}
```

When creating the tuple we're immutably borrowing slice twice int the same scope. The borrow checker doesn't know we're borrowing different parts of the slice.

We know it valid so let's use `unsafe` block here:

```rust
use std::slice;

fn split_at_mut(slice: &mut [i32], mid: usize) -> (&mut [i32], &mut [i32]) {
    let len = slice.len();
    let ptr = slice.as_mut_ptr();  // get a raw mutable pointer

    assert_eq!(mid <= len);

    unsafe {
        (
            // unsafe fn; create a new slice taking pointer to data and length
            slice::from_raw_parts_mut(ptr, mid),
            slice::from_raw_parts_mut(
                // ptr.add() return a pointer at a given offset
                ptr.add(mid), len - mid
            )
        )
    }
}
```
We know that slices are a pointer to some data and the length of that data.

{{< ref title="The Slice Type" link="/notes/rust/ownership.md" subsection="#the-slice-type" >}}

`ptr.add()` and `slice::from_raw_parts_mut()` are unsafe because it expects the poiter passed in to be valid. The function `split_at_mut()` itself is safe and can be called from safe Rust code.

## extern Functions to Call External Code
Sometimes our Rust code may need to interact with code in different language.

For this purpose Rust has `extern` keyword which facilitates the creation and use of foreign function interface, **FFI**.

<mark class="v">A foreign language interface is a way for a programming language to define a function that another language or a foreing language could call.</mark>

```rust
extern "C" {
    fn abs(input: i32) -> i32;
}

fn main() {
    unsafe {
        println!("Absolute value of -3 according to C: {}", abs(-3));
    }
}
```

Here we set up an integration with `abs()` function from C standard library. <mark class="y">Calling a function defined withing an `extern` block 'cause we don't know the language we're calling into has the same rules and guarantees as Rust.</mar>

It's developer responsibility that functions defined an extern block are safe to call. 

- Inside `extern` we specify the name and signature of the foreign function we want to call.
- The `"C"` defines which **Application Binary Interface** or **ABI** the external function uses. *ABI* defines how to call the function at the assembly level.
    
    The `"C"` *ABI* is the most common *ABI* and follows the C programming lagnuage API.

We can also allow other languages to call our Rust functions by using the `extern` keyword in the function signature:

`#[no_mangle]` annotation is required to let the Rust compiler know not to mangle the name of our function. <mark class="y">Mangling is when the compiler changes the name of a function to give it more informatioin for other parts of the compilation process.</mark>

```rust
#[no_mangle]
pub exter "C" fn call_from_c() {
    println!("Just called a Rust function from C!");
}
```

## Accessing or Modifying Mutable Static Variable
Uptil now we haven't talked about Global variables in Rust; although are supported but can cause problem with Rust ownership rules.

If two threads are accessing the same mutable global state then it could cause a data race.

In Rust global Variables are called **Static Variables**

```rust
// naming convention is to use screaming snakecase with type annotation
// with static lifetime
static HELLO_WORLD: &str = "Hello, world!";

fn main() {
    println!("name is: {}", HELLO_WORLD);
}
```

Constants and immutable static variables are similar with the difference being <mark class="y">static variables have fixed address in memory.</mark> <mark class="y">Constants are allowed to duplicate their data whenever they are used.</mark> Compiler can replace all the ocuurence of constants with concrete value.

<mark class="y">Static variables can be mutable but accessing and modifyig mutable static variables is unsafe.</mark>

```rust
static mut COUNTER: u32 = 0;

fn add_to_count(inc: u32) {
    // modification is unsafe
    unsafe {
        COUNTER += inc;
    }
}

fn main() {
    add_to_count(3);

    // accessing is unsafe
    unsafe {
        println!("COUNTER: {}", COUNTER);
    }
}
```

## Implementing an Unsafe Trait
<mark class="v">A trait it unsafe when at least one of it's method is unsafe.</mark>

```rust
unsafe trait Foo {
    // methods go here
}

unsafe impl Foo for i32 {
    // method implementation go here
}

fn main() {}
```

## Accessing Fields of a Union
A union is similar to struct but only one field is used for each instance. Unions are primarily used to interface with C unions and it's unsafe to access fields of a union because Rust cannot guarantee what the tyoe of data stored in the union is for given instance.

## Whe to Use Unsafe Code
Using unsafe isn't wrong or goes against the belief of Rust. But it's a developer responsibility to know what he/she is doing.