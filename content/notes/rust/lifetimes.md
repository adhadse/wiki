# Rust Lifetimes

[Validating References with Lifetimes](https://doc.rust-lang.org/stable/book/ch10-03-lifetime-syntax.html){ .md-button }


## The Borrow Checker
!!! info "Dangling References"

    A reference that points to invalid data.

    ```rust
    fn main() {
        let r;
        {
            let x = 5;
            r = &x;  // `x` does not live long enough
        }
        // `r` has become a dangling reference
        // since `r` goes out of scope in inner scope; get's dropped
        println!("r: {}", r);
    }
    ```

Rust is able to identify this above issue at compile time using an inbuilt feature of the compiler calld Borrow checker. It validates all borrowed values or references are valid.

Here we annotate the lifetimes of the variables in the above code.

```rust
fn main() {
    let r;                     // ----------+-- 'a
    {                          //           |
        let x = 5;             // -+---- 'b |
        r = &x;                //  |        |
    }                          // -+        |
    println!("r: {}", r);      // ----------+
}
```

<mark class="v">**Lifetime** of a variable referes to how long the variable lives.</mark>

`r` lifetime is annotated by `'a` and lives till the end of main function. Then inside inner scope, `x` lifetime is annotated by `'b` and it lives only till the end of the scope. Now with this information, borrow checker can invalidate reference `r` since `x` lives long enough only inside the inner scope.

---

```rust
fn main() {
    let x = 5;             // ----------+-- 'b
    let r = &x;            // --+-- 'a  |
                           //   |       |
    println!("r: {}", r);  // ----------+
}
```
This programs runs completely fine, no compile time error, because `x` and `r` both lives long enough till the end of main function.

## Generic Lifetime Annotations
There do arrive situations where we do need to help the compiler by specifying the lifetimes of variables.

Let's look at by examples:

```rust
fn main() {
    let string1 = String::from("abcd");
    let string2 = String::from("xyz");

    let result = longest_str(string1.as_str(), string2.as_str());
    println!("The longest string is {}", result);
}

fn longest_str(x: &str, y: &str) -> &str { // error: missing lifetime specifier
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

Here the `longest_str()` function returns a reference to string slice.

From the point of view of borrow checker, how would it know that `result` when printed in `main()` is not a dangling pointer?

The lifetime of the returned reference is determined by the if statement.

- Returning either `x` or `y` can have different lifetime.
- We also don't know the exact lifetime of `x` and `y`. `x` and `y` are just parameters to any variable existing in any part of the code

To fix this, we need to use **generic lifetime annotation**.

<mark class="y">Generic lifetime annotations (or simply called *lifetimes*) describe the relationship between the lifetimes of multiple references and how they relate to each other.</mark> They don't change the lifetime.

- Generic lifetime annotations or lifetimes always start with an apostrophe/tick.
- Lifetimes of arguments being passed in are called **input lifetimes**.
- Lifetimes of returned values are called **output lifetimes**.

Here is how you specify lifetimes:
```rust
// &i32        // a reference
// &'a i32     // a reference with an explicit lifetime
// &'a mut i32 // a mutable reference with an explicit lifetime
```

```rust
// the lifetime of the returned reference will be the same
// as the smallest lifetime of the arguments
fn longest_str<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

So, if `x` has smaller lifetime than `y` than lifetime of returned reference will be same as `x` and vice versa if `y` has smaller lifetime.

Now we told the borrow checker, whatever gets returned by `longest()` and saved in `result` will have the lifetime equal to the smallest lifetime of argument being passed in.

The borrow checker can now check if the smallest lifetime is still valid when we are trying to print.

---

Let's look at an example where the lifetimes is different with an updated `main()` function.

```rust
fn main() {
    let string1 = String::from("abcd"); // string1 lifetime will be till end of main

    {
        let string2 = String::from("xyz");
        let result = longest_str(string1.as_str(), string2.as_str());
        println!("The longest string is {}", result);
    }
}
```

Here, `result` lifetime will be same as `string2` since it has smallest lifetime being passed in `longest_str()` function which lasts till the inner scope.

`result` is still when `println!` gets called since `string2` is still valid.

But when:

```rust
fn main() {
    let string1 = String::from("abcd"); // string1 lifetime will be till end of main

    {
        let string2 = String::from("xyz");
        let result = longest_str(string1.as_str(), string2.as_str());
        //                                   error:^^^^^^^ `string2` doesn't live long enough
    }
    println!("The longest string is {}", result);
}
```

This gives us error because when we try to print out `result` with smaller lifetime equal to `string2`, it doesn't live long enough and is invalidates after the inner scope.

## Thinking in terms of lifetimes
We can define different lifetime depending on what the function is returning.

Say we want the `longest_str()` function to always return `x`. In which case we don't need to annotate the lifetime for `y`. Our code is now valid!

Why? Because we know `longest_str()` will return the reference whos lifetime is smallest and same as first parameter. And the first parameter `string1` lives till the end of `main()` before which we're calling `println!` macro.

```rust
fn main() {
    let string1 = String::from("abcd");

    {
        let string2 = String::from("xyz");
        let result = longest_str(string1.as_str(), string2.as_str());
    }
    println!("The longest string is {}", result);
}

fn longest_str<'a>(x: &'a str, y: &str) -> &'a str {
    x
}
```

!!! info "The lifetime of our return value always has to be tied to the lifetime of one our paramters."

    This is because if we return a reference from a function it has to be a reference that is something passed in. We can't return a reference to something that is created inside the function, which will be dropped once the function goes out of scope.

    So, this doesn't work:
    ```rust
    fn longest_str<'a>(x: &str, y: &str) -> &'a str {
        let result = String::from("long enough");
        result.as_str()
    }
    ```

    But this is fine, as it retuns a owned type, which transfers the ownership to caller:
    ```rust
    fn longest_str<'a>(x: &str, y: &str) -> String {
        let result = String::from("long enough");
        result
    }
    ```

## Lifetime annotatinos in struct definitions
Usually we use owned data type in structs, but if we want to use a reference then we need to specify lifetime annotations.

```rust
struct ImportantExcerpt<'a> {
    part: &'a str,
 // struct cannot outlive the reference passed into `part`
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find");
    let i = ImportantExcept {
        part: first_sentence,
    };

    // we can't use `i` once `first_sentence` goes out of scope.
}
```

## Lifetime Elision
In this code, which we previously wrote, didn't had lifetime annotation. Remember right? It worked whether or not lifetimes were annotated.

```rust
fn main() {}

// Using Lifetime elision rule 2
fn first_word<'a>(s: &'a str) -> &'a str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
}
```

So there are scenarios where compiler can deterministically infer the lifetime by checking the three lifetime elision rules:

!!! info "Lifetime Elision rules"

    1. Each parameter that is a reference gets its own lifetime parameter.
    2. If there is exactly one input lifetime parameter, that lifetime is assigned to all output lifetime parameters.
    3. If there are multiple input lifetime parameters, but one of them is `&self` or `&mut self` the lifetime of self is assigned to all output lifetime parameters.

## Lifetime Annotations in method definitions
We don't need to specify lifetimes for method `return_part()`.

```rust
struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn return_part(&self, announcement: &str) -> &str {
        println!("Attension please: {}", announcement);
        self.part
    }
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().expect("Could not find");
    let i = ImportantExcept {
        part: first_sentence,
    };
}
```

Why?

- According to rule, each reference gets a lifetime. `&self` will get a lifetime, say `'a` and `announcement` will also get one, say `'b`.
- According to second rule, the output lifetime gets assignment from exactly one input lifetime, if we have only one input parameter. Here we have two, so rule 2 doesn't apply.
- According to third rule, if one of the parameters to a function is `&self` or `&mut self` then all output lifetimes will be same as `self. Yup! This apply here.

## Static Lifetimes
**The reference could live as long as the duration of the program.**

- All string literals have static lifetimes, since they are stored in program's binary.
