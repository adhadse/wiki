---
title: "Common Collections in Rust"
description: ""
lead: ""
date: 2022-09-20T07:58:00+01:00
lastmod: 2022-09-20T07:58:00+01:00
images: []
type: docs
draft: false
menu: 
  notes:
    parent: "rust"
weight: 8
toc: true
---

Collections allow us to store multiple values, but unlike array or tuples, they are allocated on the heap. Meaning the size of the collection could grow or shrink as needed.

## Vectors
Vectors is a type of collection that can store only one type of data.
```rust
fn main() {
    let a = [1, 2, 3]; // array
    
    let mut v: Vec<i32> = Vec::new(); // empty vector
    // a vector can grow
    v.push(1);
    v.push(2);
    v.push(3);

    // create vector using macro with value
    let v2 = vec![1, 2, 3];
}
```

### Access elements
```rust
fn main() {
    let v = vec![1, 2, 3, 4, 5];

    let third = &v[2]; // a reference to vector
    println!("The third element is {}", third);
}
```
If we try to access out-of-bound element, the program panics and we get a run time error.

```rust
let third = &v[20];
```

```text
thread 'main' panicked at 'index out of bounds: the len is 5 but the index is 20', src/main.rs:4:18
```

If we had used array and tried to access index that was out of bounds, we'd get compile time error, program would'nt even run. This is because with the arrays the size is fixed and knows at compile time but not with vectors.

{{< alert type="warning" title="Don't use index to access elements of vector" >}}
{{< /alert >}}

{{< alert type="success">}}
Insead use the `get` method to gracefully handle the out-of-bound index which returns an [`Option`](/notes/rust/enums-and-pattern-matching-in-rust/#the-option-enum) Enum.
{{< /alert >}}

```rust
match v.get(2) {
    Some(third) => println!("The third element is {}", third),
    None => println!("There is no third element.")
}
```

We know that an immutable or mutable reference to an item can't exist at the same time. So if we wanted to push an element `third` before printing it out:

```rust
let third = &v[2];
// error. Cannot borrow `v` as mutable because it is also borrows as immutable
v.push(6); 
println!("The third element is {}", third);
```

This is because when we need to add element to a vector, we might need to allocate more memory if the vector is full. In that case `third` will go invalid pointing to unknown memory address. 

---
### Iterating over elements
Let's iterate over all elements and print them.

```rust
fn main() {
    let mut v: vec![1, 2, 3, 4, 5];

    // take a immmutable reference of each element
    for i in &v {
        println!("{}", i);
    }

    // take a mutable reference
    for i in &mut v {
        *i +=50; // dereference operator and add 50
    }
}
```
---
### Storing Enum varients inside of a vector
A `row` stores `SpreadsheetCell` type with different varients.
```rust
fn main() {
    enum SpreadsheetCell {
        Int(i32),
        Float(f64),
        Text(String),
    }

    // you are allowed to store an Enum type with different varients
    let row: Vec<SpreadsheetCell> = vec![
        SpreadsheetCell::Int(3),
        SpreadsheetCell::Text(String::from("blue")),
        SpreadsheetCell::Float(10.12),
    ]

    // the catch is when you reference a specific element inside
    // of vector we need to use a match expression to figure 
    // out which varient of Enum it is.
    // since we're storing Enum inside
    match &row[1] {
        SpreadsheetCell::Int(i) => println!("{}", i),
        _ => println!("Not a integer!")
    }
}
```

## Strings
<mark class="y">Strings are stored as a collection of UTF-8 encoded bytes.</mark>
- In memory a string is just a list or a collection 1s and 0s. Now a program needs to be able to interpret 1s and 0s and print out the correct characters, that's were encoding comes into play.
- ASCII or American Standard code for Information Interchange is a character encoding and decoding (1s and 0s to string and back). Although it can only represent 128 characters which includes english alphabet, some special characters

    - Since ASCII can't represent other language characters, others countries created their own encoding standards for their own languages.
    - <mark class="r">This becomes problematic since how a program will know which encoding standards to use to parsing a collection of bytes</mark>
    - <mark class="g">To solve this Unicode was created which represent a wider array of characters from all well-known languages, emojis and is also backwards compatible with ASCII.</mark>
- UTF-8 is a variable-width character encoding. Variable because it can be represented as one bytes, two bytes, three bytes or four bytes.<mark class="v">UTF-8 is a very popular encoding of Unicode.</mark>

```rust
fn main() {
    let s1: String = String::new();    // empty String
    let s2: &str = "initial contents"; // creating string slices
    let s3: String = s2.to_string;     // turn into owned String
    let s4: String = String::from("initial commit");
}
```

Strings are UTF-8 encoded, so you can represent other languages as well.
```rust
fn main() {
    let hello = String::from("안녕하세요");
    let hello = String::from("नमस्ते");
    let hello = String::from("こんにちは");
    let hello = String::from("你好");
    let hello = String::from("Hello");
    let hello = String::from("Dobrý den");
    let emoji = String::from("😼");
}
```

### Appending to a String
```rust
fn main() {
    let mut s = String::from("foo");
    s.push_str("bar"); // takes a string slice to avoid owning it
    s.push('!'); // append characers
    // foobar!
}
```

```rust
fn main() {
    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");

    // moving ownership of `s1` into `s3` and taking all 
    // characters of `s2` append them at end
    let s3: String = s1 + &s2;
}
```

```rust
fn main() {
    let s1 = String::from("Hello, ");
    let s2 = String::from("world!");

    // contatenate using format macro
    let s3 = format!("{}{}", s1, s2);
}
```

### Indexing into string
```rust
fn main() {
    let hello = String::from("hello");
    // error!
    // the type `String` cannot be indexed by `{integer}`
    // the trait `Index<{integer}>` is not implemented for `String`
    let c: char = hello[0]; 
}
```

String is a collection of bytes. What is the length of `hello` here? Well, 5. But what would be the length of `hello` in this case, hello in Hindi:.

```rust
let hello = String::from("नमस्ते");
```

5? Nope, the length is 18. 

Or in this case:

```rust
let hello = String::from("안녕하세요");
```
12? Nope, 15.

In UTF-8 strings could be 1 to 4 bytes long. So getting the first character in the string using `[]` syntax would not work because `hello[0]` only specifies the first byte in our collection of bytes

### Representation of word in Unicode
Let's understand the three Relevant ways a word in represented in unicode.

Rust doens't know what we want to receive; Byes, scalar values or grpheme clusters. For that we need special methods.

```rust
fn main() {
    let hello = String::from("नमस्ते");
    // Bytes
    // [224, 164, 168, 224, 164, 174, 224, 164, 184, 224, 165, 141, 224, 164, 164, 224, 165, 135]

    // Scalar values (`char` type): represent full or parts of characters
    // ['न', 'म', 'स', '्', 'त', 'े']

    // Grapheme clusters: what every hooman consider as character
    // ["न", "म", "स्", "ते"]
}
```

```rust
use unicode_segmentation::UnicodeSegmentation;

fn main() {
    let hello = String::from("नमस्ते");

    // Ierating over bytes
    for b in hello.bytes() {
        println!("{}", b);
    }
    // or
    println!("{:?}", String::from("नमस्ते").as_bytes());

    // Iterating over Scalar value
    for c in hello.chars() {
        println!("{}", c);
    }

    // Iterating over Grapheme clusters is not present by default 
    // to keep the standard library clean and lean.
    // this requires an external crate: `unicode-segmentation`
    // `true` to get extended grapheme
    for g in hello.graphemes(true) {
        println!("{}", g);
    }
}
```

## Hashmaps
Stores keys, values pair.

We need to bring in `HashMap` from Rust standard library

### Inserting and extracting values from HashMap
```rust
use std::collections::HashMap;

fn main() {
    let blue = String::from("Blue");
    let yellow = String::from("Yellow");

    let mut scores = HashMap::new();

    // move value of strings; taking ownership
    // If we didn't want the HashMap to take ownership of our String, 
    // We could pass reference to string, but that would have required lifetimes.
    scores.insert(blue, 10);
    scores.insert(yellow, 50);

    // To get values back, pass reference to String (or string slice)
    // this returns an Option enum, 
    // because we can't gurantee a value will be returned
    let score = scores.get(&String::from("Blue"));
    let score = scores.get("Blue");
}
```

### Iterating 
```rust
use std::collections::HashMap;

fn main() {
    // defines `scores` and insert values
    for (key, value) in &scores {
        println!("{}: {}", key, value)
    }
}
```

### Updating hashmap
```rust
use std::collections::HashMap;

fn main() {
    let mut scores = HashMap::new();

    scores.insert(String::from("Blue"), 10);
    scores.insert(String::from("Blue"), 20); // override the original value


    // if don't want to override
    // `entry` gives an Entry enum representing value for given key
    // If an entry `Yellow` doesn't exist then insert one with value 30; otherwise do nothing
    scores.entry(String::from("Yellow")).or_insert(30);
    scores.entry(String::from("Yellow")).or_insert(40); // won't override
}
```

### Updating value based on old value
Here we're are populating `map` with word count
```rust
use std::collections::HashMap;

fn main() {
    let text = "hello world wonderful world";

    let mut map = HashMap::new();

    for word in text.split_whitespace() {
        let count: &mut i32 = map.entry(word).or_insert(0);
        *count += 1;
    }

    println!("{:?}", map);
}
```
Output:

```text
{"world": 2, "hello": 1, "wonderful": 1}
```