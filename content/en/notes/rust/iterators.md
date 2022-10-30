---
title: "Iterators in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:06+01:00
lastmod: 2022-09-20T07:58:06+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 14
toc: true
---

{{< alert >}}
Iterator pattern allows us to iterate over a sequence of elements regardless of how the elements are stored.
{{< /alert >}}

## Processing items with Iterators
Iterators can be implemented for any data structure.

```rust
fn main() {
    let v1 = vec![1, 2, 3];

    // iterators are lazy in Rust
    let v1_iter = v1.iter();

    // abstract away the logic of how to iterate over the sequence
    // encapsulated by iterator
    for value in v1_iter {
        println!("Got: {}", value);
    }
}
```


## Iterator Trait and the next Method
All iterators in Rust implements `Iterator` trait defined in standard library, something like this:

The `next()` method returns the next Item in the sequence and requires a mutable reference to self because calling `next()` changes the internal state of iterator used to track where it is.

```rust
pub trait Iterator {
    type Iterm;    // Associated types

    fn next(&mut self) -> Option<Self::Item>;

    // methods with default implementations elided
}

#[test]
fn iterator_demonstration() {
    let v1 = vec![1, 2, 3];

    // an immutable reference
    let mut v1_iter = v1.iter();

    // for mutable references use `iter_mut()`

    assert_eq!(v1_iter.next(), Some(&1));
    assert_eq!(v1_iter.next(), Some(&2));
    assert_eq!(v1_iter.next(), Some(&3));
    assert_eq!(v1_iter.next(), None);
}
```

## Methods that Consume the iterator
Iterator trait has various methods with default implementations.

There are two broad categories:
1. **Adaptors**: <mark class="y">take in an and return another iterator</mark>
2. **Consumers**: <mark class="y">take in an iterator and returns some other type.</mark>

For example `sum()` is a type of consumer, which repeatedly calls `next()` method to get next element and add them up:

```rust
#[test]
fn iterator_sum() {
    let v1 = vec![1, 2, 3];
    let total: i32  = v1.iter().sum();
    assert_eq!(total, 6);
}
```

## Methods that Produce Other Iterators
Adapter methods produce other iterators, one of them is `map()` which takes in a closure and returns an iterator which calls the closure over each element in sequence:

```rust
fn main() {
    let v1: Vec<i32> = vec![1, 2, 3];
    v1.iter().map(|x| x+1);
}
```

Since in Rust iterators are lazy, the compiler will warn about the iterator that is not used returned by `map()` and this won't actually do anything until a consumer method is called upon:

```rust
fn main() {
    let v1: Vec<i32> = vec![1, 2, 3];
    let v2: Vec<_> = v1.iter().map(|x| x+1).collect();

    assert_eq!(v2, vec![2, 3, 4]);
}
```

## Closures that capture their Environment

```rust
#[derive(PartialEq, Debug)]
struct Shoe {
    size: u32,
    style: String,
}

// returns shoes vector that have `shoe_size`
//
// `shoe_size` in closure passed into the `filter()`
// method can be accessed from the environment
fn shoes_in_my_size(shoes: Vec<Shoe>, shoe_size: u32) -> Vec<Shoe> {
    // the iterator `into_iter()` take ownership of our vector
    shoes.into_iter().filter(|s| s.size == shoe_size).collect()
}

fn main() {}

#[cfg(test)]
mod tests {
    user super::*;

    $[test]
    fn filters_by_size() {
        let shoes = vec![
            Shoe {
                size: 10,
                style: String::from("sneaker"),
            },
            Shoe {
                size: 13,
                style: String::from("sandal")
            },
            Shoe{
                size: 10,
                style: String::from("book"),
            },
        ];

        let in_my_size = shoes_in_my_size(shoes, 10);

        assert_eq!(
            in_my_size,
            vec![
                Shoe {
                size: 10,
                style: String::from("sneaker"),
                },
                Shoe{
                size: 10,
                style: String::from("book"),
                },
            ]
        )
    }
}
```

## Creating our own iterators

```rust
struct Counter {
    count: u32,
}

impl Counter {
    fn new() -> Counter {
        Counter { count: 0 }
    }
}

impl Iterator for Counter {
    type Item = u32;

    // the only method we need to implement
    fn next(&mut self) -> Option<Self::Item> {
        if self.count < 5 {
            self.count += 1;
            Some(self.count)
        } else {
            None
        }
    }
}

// a test for our `next()` method
#[test]
fn calling_next_directly() {
    let mut counter = Counter::new();

    assert_eq!(counter.next(), Some(1));
    assert_eq!(counter.next(), Some(2));
    assert_eq!(counter.next(), Some(3));
    assert_eq!(counter.next(), Some(4));
    assert_eq!(counter.next(), Some(5));
    assert_eq!(counter.next(), None);
}
```

Few other methods of `Iterator` traits:
1. `zip()`: 'Zips up' two iterators into a single iterator of pairs.
    The first iterator is the one on which `zip()` is called on, the second is being passed into the method.
2. `skip()`: Is an adapter method returns iterator, skipping first `n` elements.
3. `map()`: Takes a closure and call it for each item in the iterator.
4. `filter()`: filter item by taking in a closure, requiring to return a `bool` value to be accepted into the generated iterator.
5.  `sum()`: cosumer method to sum up all values.

```rust
#[test]
fn using_other_iterator_trait_methods() {
    let sum: u32 = Counter::new()
        .zip(Counter::new().skip(1)) 
        .map(|(a, b)| a*b)      // a pair of value from previous `zip` iterator
        .filter(|x| x%3 == 0)
        .sum();
    asser_eq!(18, sum);
}
```
