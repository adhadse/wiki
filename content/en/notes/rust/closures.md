---
title: "Closures in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:09+01:00
lastmod: 2022-09-20T07:58:09+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 13
toc: true
---
{{< alert title="What are closures?" >}}
Closures are kind of function but anonymous (unnamed), have ability to be stored as variables and passed as input parameters to others functions.
{{< /alert >}}

## Example Program
Let's say we are creating a backend for a fitness that generates customized workouts for a user based on various health factors. Now part of this system might perform some really expensive calculation. Something like this:

```rust
use std::thread;
use std::time::Duration;

fn simulated_expensive_calculation(intensity: u32) -> u32 {
    println!("Calculating slowly...");
    thread::sleep(Duration::from_secs(2));
    intensity
}

fn main() {
    let simulated_intensity = 10;    // some number coming in from user input; here just hardcoded
    let simulated_random_number = 7; // provide a variety in generated workout

    // generate a workout 
    generate_workout(simulated_intensity, simulated_random_number);
}

fn generate_workout(intensity: u32, random_number: u32) {
    if intensity < 25 {
        println!(
            "Today, do {} pushups!", 
            simulated_expensive_calculation(intensity)
        );
        println!(
            "Next, do {} situps!",
            simulated_expensive_calculation(intensity)
        );
    } else {
        if random_number == 3 {
            println("Take a break today! Rember to stary Hydrated!");
        } else {
            println!(
                "Today, run for {} minutes!", 
                simulated_expensive_calculation(intensity)
            );
        }
    }
}
```

## Refactoring with functions
We are calling our expensive function at multiple places, if we change the function definition, a lot of refactoring will be required. Plus we are calling the expensive function repetitvely.

Let's refactor it:

```rust
fn generate_workout(intensity: u32, random_number: u32) {
    let expensive_result = simulated_expensive_calculation(intensity);
    if intensity < 25 {
        println!("Today, do {} pushups!", expensive_result);
        println!("Next, do {} situps!", expensive_result);
    } else {
        if random_number == 3 {
            // but we don't need a call our expensive function if random number is 3
            println("Take a break today! Rember to Hydrated!");
        } else {
            println!("Today, run for {} minutes", expensive_result );
        }
    }
}
```

## Refactoring using Closures
Closure help keep the logic at one place while keeping it anonymous.

But the problem of calling the expensive operation remains in first `if` block. 

```rust
fn generate_workout(intensity: u32, random_number: u32) {
    // `num` is the input parameter inside | | 
    // if closure is just one life you don't need {}
    //
    // `expensive_closure` don't store the return value, but the closure
    let expensive_closure = |num| {
        println!("Calculating slowly..");
        thread::sleep(Duration::from_secs(2));
        num
    };

    // BUT we're still calling expensive operation twice!
    if intensity < 25 {
        println!("Today, do {} pushups!", expensive_closure(intensity));
        println!("Next, do {} situps!", expensive_closure(intensity));
    } else {
        if random_number == 3 {
            // but we don't need a call our expensive function if random number is 3
            println("Take a break today! Rember to Hydrated!");
        } else {
            println!("Today, run for {} minutes",  expensive_closure(intensity)) );
        }
    }
}
```

{{< alert type="success" title="Why no type annotation for closure's input parameters?" >}}
Functions provide explicity interface exposed to users so agreeing on the types of inputs are return values are important.

Closures on the other hand are relevant in a much narrow context and so compiler happily determines the input and output types.
- The first type being passed in to the closure becomes the concrete type of the paremeter. There is no dynamic typing.
{{< /alert >}}

## Generic Parameters and Fn Traits
We could have solved the problem of calling the expensive function multiple times by storing the result in a variable.

**But, we can do better**.

We'll use **Memoization** pattern, by creating a struct to hold the closure and the result of our closure with generic type `T` bounded by trait `Fn`.

`Fn` trait is provided by standard library and all closures (and regular functions) implement one of the three `Fn` traits:
1. `Fn`: immutable borrows values.
2. `FnMut`: mutably borrows values.
3. `FnOnce`: takes ownershup of the variables inside the closure. `Once` here indicates that closures are not allowed to take ownership of same variables more than once. <mark class="y"> Meaning this closures can only be called once.</mark>

```rust
struct Cacher<T>
where 
    T: Fn(u32) -> u32,
{
    calculation: T,     // the calculation function
    value: Option<u32>  // stored calculated value
}
```

```rust
impl<T> Cacher<T>
where
    T: Fn(u32) -> u32,
{
    fn new(calculation: T) -> Cacher<T> {
        Cacher {
            calculation,
            value: None
        }
    }

    // when we first create our cacher, `value` will be none,
    // so match expression allow us to handle the variant of the 
    // `Option` and set the value after calling `calculation` closure.
    fn value(&mut self, arg: u32) -> u32 {
        match self.value {
            Some(v) => v,
            None => {
                let v = (self.calculation)(arg);
                self.value = Some(v);
                v
            }
        }
    }
}
```

Let's use our `Cacher` struct in `generate_workout()` function.

We'll wrap the closure in `Cacher` struct:

```rust
fn generate_workout(intensity: u32, random_number: u32) {
    let mut cached_result = Cacher::new(|num| {
        println!("Calculating slowly..");
        thread::sleep(Duration::from_secs(2));
        num
    });
 
    if intensity < 25 {
        println!("Today, do {} pushups!", 
        cached_result.value(intensity));
        println!("Next, do {} situps!", 
        cached_result.value(intensity));
    } else {
        if random_number == 3 {
            println("Take a break today! Rember to Hydrated!");
        } else {
            println!("Today, run for {} minutes", 
            cached_result.value(intensity)) );
        }
    }
}
```

This works, but what we might want to do is instead of caching one value no matter what the `arg` passed in is; <mark> we need to cache one value for each `arg` being passed because `arg` changes the value.</mark>

This requires hashmap, where the keys will be argument passed into `value()` and value will be the result of calling the closure `calculation` if not already in the hashmap. 

We might also want to use generic function for our closure instead of hard coding the type to `u32`.

```rust
use std::collections::HashMap;
use std::hash::Hash;

struct Cacher<F, K, V> {
    calculation: F,
    cache: HashMap<K, V>,
}

impl<F, K, V> Cacher<F, K, V>
where
    F: Fn(&K) -> V,
    K: Hash + Eq,
{
    fn new(calculation: F) -> Self {
        Cacher {
            calculation,
            cache: HashMap::new(),
        }
    }

    fn value(&mut self, arg: K) -> &V {
        use std::collections::hash_map::Entry;

        match self.cache.entry(arg) {
            Entry::Occupied(occupied) => occupied.into_mut(),
            Entry::Vacant(vacant) => {
                let value = (self.calculation)(vacant.key());
                vacant.insert(value)
            }
        }
    }
}
```

## Capturing the environment with closure
Unlike functions, closure have access the variables that are defined within the scope in which the closure is defined. This are required extra memory overhead than regular functions.

```rust
fn main() {
    let x = 4;

    // closure saved in `equal_to_x` has access to `x`
    let equal_to_x = |z| z == x;

    let y = 4;

    assert!(equal_to_x(y));
}
```

Closures capture variables from there environment in three ways, encoded in function traits we talked earlier:
1. By borrowing immutably `Fn`
2. By borrowing mutably   `FnMut`
3. By taking ownership    `FnOnce`

When we create closures Rust automatically infers which traits to use based on how you use the values inside the closures environment.

<mark class="v">We can force the closure to take ownershup of the values it uses inside it's environemnt by using the `move` keyword in front of closure.</mark> (userful when passing closure from one thread to another)

```rust
fn main() {
    let x = vec![1, 2, 3];

    // this will work though, since it doesn't take ownership of `x`
    // let equal_to_x = |z| z == x;
    // this won't:
    let equal_to_x = move |z| z == x;

    println!("Can't use x here: {:?}", x);
    //                                 ^ error: borrow of moved value

    let x = vec![1, 2, 3];

    assert!(equal_to_x(y));
}
```