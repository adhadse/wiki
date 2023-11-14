# Common Programming Concepts in Rust


[Common Programming Concepts](https://doc.rust-lang.org/stable/book/ch03-00-common-programming-concepts.html){ .md-button }

## Variables and mutability
Variables are immutable by default. I said it.

```rust
fn main() {
    let x = 5;
    println!("The value of x is {}", x);
    x = 42;
    println!("The value of x is {}", x);
}
```
This will throw error, stating, cannot assign twice to immutable variable `x`.

```text
error[E0384]: cannot assign twice to immutable variable `x`
 --> src/main.rs:4:5
  |
2 |     let x = 5;
  |         -
  |         |
  |         first assignment to `x`
  |         help: consider making this binding mutable: `mut x`
3 |     println!("The value of x is {}", x);
4 |     x = 42;
  |     ^^^^^^ cannot assign twice to immutable variable

For more information about this error, try `rustc --explain E0384`.
error: could not compile `playground` due to previous error
```

Make it mutable as we learned:

```rust
let mut x = 5;
```
### Constant
Values that never changes, create it by using `const` keyword (make sure to provide a type as well, it's required):

```rust
const MINUTES_IN_YEAR: i32 = 5_25_600;
```

So, **why do we require constants, when we already have immutable variables?**

!!! info "Constants v/s variables"

      1. We cannot mutate a constant. `mut` keyword is invalid with `const`.
      2. `const`s must also be type annotated.
      3. `const` can also be set to constant expressions. We cannot assign return value of functions to them.

### Shadowing
Shadowing allows us to create new variables using an existing name.

The below code is valid:

```rust
let x = 5; // This gets shadowed by second `x`
let x = 42;
```
!!! "Advantages of shadowing"

    1. We can preserve immutability.

        Both `x` in above example remains immutable.

    2. We can change type.

       ```rust
       let x = 5;
       let x = "six";
       ```

## Data Types
We have two types of Data Types:
1. **Scalar data types**: represent a single value
2. **Compound data types**: represent a group of values

### Scalar data types:
1. Integers: Numbers without a fractional component

| Length   | Signed   | Unsigned |
| ---      | ---      | ---      |
| 8-bit    | `i8`     | `u8`     |
| 16-bit   | `i16`    | `u16`    |   
| 32-bit   | `i32`    | `u32`    |
| 64-bit   | `i64`    | `u64`    |
| 128-bit  | `i128`   | `u128`   |
| arch (architecture based)    | `isize`  | `usize`  |

Signed integers can be positive or negative, unsigned are positive only. By default rust uses signed 32 bit integer. 

```rust
fn main() {
    let a = 98_222; // Decimal
    let b = 0xff;   // Hex
    let c = 0o77;   // Octal
    let d = 0b1111_0000; // Binary
    let e = b'A';   // Byte (u8 only)

    // Any value greater than what it can hold will
    // in Debug builds will panic
    // in Release builds will wrap around back to minimum 
    // i.e., perform 2s Complement wrapping
    let f: u8 = 255;
}
```

2. Floating point numbers

```rust
fn main() {
    let f = 2.0;     // defaults to f64
    let g: f32 = 3.0;
}
```

3. Booleans

```rust
fn main() {
    let t = true;
    let f: bool = false;
}
```

4. Characters: represent unicode characters

```rust
fn main() {
    let c = 'z';
    let z = 'Z';
    let heart = '♥';
}
```

### Compound Data Types
1. Tuples: A tuple is a collection of values of different types constructed using paranthesis.

```rust
fn main() {
    let tup = ("Hello, World!", 100_000);

    // To get values of tuple
    // 1. Destructuring
    let (str_var, int_var) = tup;

    // 2. Dot notation
    // tuples and array start at index 0
    let int_var  = tup.1;
}
```

2. Arrays: An array is a fixed length collection of objects of the same type T, stored in contiguous memory, constructed using bracked [].

```rust
fn main() {
    let http_err_codes = [200, 404, 500];
    let res_not_found = error_codes[1];

    // create array of size 8, all set to 0
    let byes = [0; 8];
}
```

## Functions
Function naming scheme specifies that functions should named in snake case, all in lower case characters.

```rust
fn main() {
    my_function(11, 22);
}

fn my_function(x:i32, y:i32) {
    println!("Value of x: {}", x);
    println!("Value of y: {}", y);
}
```

In Rust, we can think of any piece of code as either a statement or an expression.

1. <mark class="y">Statements perform some action but do not return a value</mark>
2. <mark class="y">Expressions returns a value</mark>

We can return values in two ways:
1. either using `return` keyword and specifying return types of function at the end of decalaration.

```rust
fn my_function(x:i32, y:i32) -> i32 {
    println!("Value of x: {}", x);
    println!("Value of y: {}", y);
    let sum = x + y;
    return sum
}
```

2. or inside a function the last expression is implicityly returned. So something like this is also ok:

```rust
fn my_function(x:i32, y:i32) -> i32 {
    println!("Value of x: {}", x);
    println!("Value of y: {}", y);
    x + y
}
```

## Control Flow
### if-else statements
```rust
fn main() {
    let number = 5;

    // conditions needs to be explicitly stated
    if number < 10 {
        println!("smaller than 10");
    } else if number < 22 {
        println!("smaller than 22");
    } else {
        println!("Condition was false");
    }
}
```

We can also use `if-else` statement inside of `let` statement.

```rust
fn main() {
    let condition = true;
    let number = if condition { 5 } else { 6 }; 
}
```

### Loops
This code below can loop infinitely unless we call `break`.
```rust
fn main() {
    loop {
        println!("again");
        break;
    }
}
```

We can also return values from these loops:
```rust
fn main() {
    let mut conter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter;
        }
    };

    println!("The result is {}", result);
}
```

**While loop**
```rust
fn main() {
    let mut number = 3;
    while number != 0 {
        println!("{}", number);
        number -= 1;
    }

    println!("LIFTOFF!!!");
}
```

**For loop**
```rust
fn main() {
    let a = [10, 20, 30, 40, 50];

    // for every element in `a` without giving 
    // ownership to for loop. 
    // we'll learn more about Ownership later on
    for element in a.iter() {
        println!("the value is: {}", element);
    }

    // loop over range, exclusive
    for number in 1..4 {
        println!("Range element: {}", number);
    }
}
```

## Comments
You usually comment in Rust in either of the below two ways:
```rust
fn main() {
    // Line comment

    /*
        Block comment
    */
}
```