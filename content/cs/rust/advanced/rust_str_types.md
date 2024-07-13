# All Rust String Types explained
Unlike other languages, Rust str types comes in many flavours[^1]:

[^1]: Content from *Let's Get Rusty*'s Video:https://www.youtube.com/watch?v=CpvzeyzgQd


1. `&Str`
2. `String`
3. `&[u8; N]`
4. `Vec[u8]`
5. `Cow<'a, str>`
6. `CStr`
7. `OsStr`
8. `OSString`
9. `Path`
10 `PartBuff`

## String Fundamentals
In programming, everything is fundamentally binary data represented via 1's and 0's. For a program to convert this binary data into a human readable string, it needs two things:

1. The encoding used
2. Length of the string

### Encoding
Binary data is typically processed as a sequence of bytes, each byte containing 8 bits. Each byte can be represented as an integer using a binary number system.
<mark class="y">A character encoding is simply a standard for maping bytes to characters.</mark>

There are two common encodings you probably already heard of:

1. ASCII: Stands for *American Standard Code for Information Interchange* very simple standard dating back to 90's.

    ASCII's simplicity is also it's limiting factor, and can only represent 256 characters. And as such, can only represent english alphabet symbols and control characters and has no support for other languages or emoji/emoticons.

    <figure>
      <img src="/assets/images/cs/rust/ASCII-Table.png"></img>
      <figcaption>(source: Wikipedia)</figcaption>
    </figure>

2. UTF-8: UTF-8 short for *Unicode Transformation Format-8* is a variable length encoding where characters can go from 1 to 4 bytes, allowing us to encode multiple languages characters and complex characters like emojis. UTF-8 is widely adopted and is currently the standard for character encoding.

Now with this information, string is a sequence of bytes that lives within the memory.

When you create a string in your program, you basically create a pointer to the first bytes of the string, but how do you know where the string end? You can device two methods:

1. Traverse the string bytes-by-byte until you read a termination character, commonly called null byte. Incurrs a runtime cost for certain operations.
2. Or store the length of string along with the pointer to the first byte of the string in a higher level data structure. This gives the benefit for certain operations, such as retrieving the string length will be done in constant time, trade off being, use of more memory.

## Strings in C
Let's understand why strings in C is really simple but also makes it dangerous.

In C, string is represented as an array of character:

```c
int main() {
    char my_string[] = "Hello, World!";

    return 0
}
```

or a pointer pointing to the first character in the string:

```c
int main() {
    char my_string[] = "Hello, World!";

    char* string_ptr = my_string;

    return 0
}
```

```c hl_lines="2"
int main() {
    char my_string[] = "Hello, World!\0";   // (1)

    char* string_ptr = my_string;

    return 0
}
```

1. A null terminator is automatically added by the compiler at the end of the string.

C doesn't enfore any encoding and developer is supposed to enforce it. If your program takes in an invalid input say, invalid utf-8 characters, or your validation isn't done properly, can lead to data corruption or security vulnerabilities.

Take a look at this example, this can lead to data corruption, undefined behavior, security vulnerabilities or system crashes.

```c
int main() {
    char my_string[] = "Hello, World"; // 12 characters

    char buffer[16];  // Buffer is one character (null terminator) short
    strcpy(buffer, my_string);

    printf("The copied string is: %s\n", buffer);
    return 0;
}
```

## Strings in Rust
Let's see how Rust handle string with _safety_ in mind:

1. No null terminator: Rust stores the string length as metadata instead of null terminator, leading to more efficient runtime operations and prevent vulnerabilities like buffer overflows.
2. All strings are valid UTF-8: Rust guarantees string to be a valid UTF-8 encoded, ensuring string are intercompatible with languages and prevents issues like data corruption.
3. Immutable by default: strings or more generally variables in rust are immutable by default, ensuring that the content of the strings are changed unexpectedly.

### Strings and &str
`String` and `&str` (called string slices) are two most fundamental string types in Rust.

`String` type is heap allocated and hence growable, UTF-8 encoded string.

- It's an owned type, since it owns the underlying data
- responsible for deallocating the underlying data when the string variable goes out of scope.

```rust
let my_string: String = String::from("Hello!");
```

<mark class="v">This type consists of a pointer to the data on the heap, it's length and it's capcity.</mark>

**String slices**

<mark class="y">String slices (`&str`) on the other hand is a view into a string it represents.</mark> It represents a cotiguous sequence of UTF-8 encoded bytes.

- It's called a borrow type, as it doesn't own the underlying data. Instead it simply has access to it.
- <mark class="v">It's only holds the pointer to the starting byte of the data and the length.<mark>
- They also doesn't have a `capacity`, since they are not growable.
- They can reference data on the heap or in the data section of the compiled binary (which is the case for string literals) or strings stored on stack.

```rust hl_lines="2"
let my_string: String = String::from("Hello!");
let my_str: &str = &my_string;
```

Use case:
1. `String` is useful when you want to create or modify string data dynamically at runtime.
2. `&str` is useful when you want to read or analyze pre-existing string data without making changes to it.

### `&'static str`
Now let's see how Rust handle string with efficiency & flexibility in mind:

This is an example of string literal, which is a reference to string slice. String literals are stored in compiler's binary.

```rust
let hello: &str = "Hello, world!";
```
This is actually just a syntactic sugar for a reference with static lifetime.

```rust
let hello: &'static str = "Hello, world!";
```

<mark class="v">A static lifetime indicates that the data being pointed to is guaranteed to be available during the entirity of the program execution.</mark>

You don't need to explicity write out the static lifetime, except in certain cases, for e.g.:

- When storing string slices in structs or enums:

    ```rust
    #[dervice(Debug]
    enum MyError {
        IoErrror,
        ParseError(&'static str),
    }
    ```
- when, returning a string slice from a function that has no other borrowed paramter.

  ```rust
  fn get_greeting(hour: u8) -> &'static str {
      if hour < 12 {
          "Good Morning"
      } else if hour < 18 {
          "Good Afternnon!"
      } else {
          "Good evening!"
      }
  }
  ```

### `Box<str>`
You may notice `&str` is made up two parts: `str` represents a dynamically sized sequence of UTF-8 encoded bytes, in other words `str` describes a string slice. We can't use it directly as a standalone type, because it's size is not known at compile time. Instead we have to use `str` behind some type of pointer: `&str`, creating a reference.

<mark class="y">There are other types of string slice as well:</mark>

We can wrap the `str` type in [`Box` smart pointer](/cs/rust/tutorial/smart-pointers/box-smart-pointer/): `Box<str>`.

<mark class="v">`Box<str>` represents a string slice which is:

1. <mark class="v">Owned,</mark>
2. <mark class="v">Non-growable,</mark>
3. <mark class="v">Heap allocated</mark>

Useful when you want to freeze a `String` to avoid extra modification or save memory by dropping the extra capacity information.

```rust
let my_string: String = String::from("This is a long string, needs no modification");

// convert the String to a Box<str>
let my_boxed_str: Box<str> = my_string.into_boxed_str();

println!("My boxed str: {}", my_boxed_str);
```

### `Rc<str>`
We can also use `str` with [`Rc` (reference counting) smart pointer](/cs/rust/tutorial/smart-pointers/reference-counting/): `Rc<str>`.

<mark class="v">`Rc<str>` represents a string slice which is:

1. <mark class="v">shared,</mark>, to allowing sharing between parts of program without cloning the actual data.
2. <mark class="v">Immutable</mark>


```rust
use str::rc::Rc;

fn main() {
    let some_large_text: &'static str = "This is some large text that we need to work with.";

    // Extract a subsection that multiple parts of the program will need to reference
    let subsection: Rc<str> = Rc::from(&some_large_text[5..24]);

    // Simulate multiple owners by cloning the Rc pointer
    let another_reference = Rc::clone(&subsection);
    let yet_another_reference = Rc::clone(&subsection);

    println!("First reference: {}", subsection);
    println!("Second refernce: {}", another_reference);
    println!("Third reference: {}", yet_another_reference);
}
```

### `Arc<str>`
Atomic refernce counting smart pointer, unlike `Rc` smart pointer, <mark class="y">`Arc` is thread safe.</mark>

<mark class="v">`Arc<str>` represents a string slice which is:

1. <mark class="v">shared,</mark>, to allowing sharing between parts of program without cloning the actual data.
2. <mark class="v">thread-safe,</mark>
3. <mark class="v">Immutable</mark>

Allows us to share the `str` across threads, without having to clone the data.

```rust
fn main() {
    let tet_string = String::from("This is some text taht multiple threads will read.");
    let text_slice = &text_string[..];  // this also doesn't have 'static lifetime

    // Convert it to an Arc<str>
    for _ in 0..3 {
        let text_ref = Arc::clone(&shared_text);
        let handle = thread::spawn(move || {
            println!("Thread is reading: {}", text_ref)
        })
    }

    for handle in handles {
        handle.join().unwrap();
    }
}
```

### `Vec[u8]` & `&[u8]`
The `String` type is basically a wrapper around `Vec[u8]` the difference being, the `String` type gurantees to be a valid UTF-8.

This allows the `String` type to provide methods that make it convenient to work with unicode text and safe manipulation of underlying data.

<mark class="y">We can use Vector of bytes `Vec[u8]` or slice of bytes `&[u8]` can be useful when creating string from binary data or with strings which uses encodings other than UTF-8.</mark>

```rust
fn latin1_to_string(latin1_data: &[u8]) -> String {
    latin1_data.iter().map(|&c| c as char).collect()
}

fn main() -> io::Result<()> {
    // Read Latin-1 data into a Vec<u8>
    let latin1_data: Vec<u8> = read_latin1_string()?;

    // Convert Latin-1 data to a UTF-8 Rust String
    let utf8_string: String = latin1_to_string(&latin1_data);

    println!("Converted string: {}", utf8_string);

    Ok(());
}
```

### String literal representations (`&[u8; N]`)
1. Raw string literals: allows us to write special characters like back slashes without need of escape character. They are creating by starting the string with `r` and adding a `#` hash symbol on either side of string literal.

    ```rust
    let text = "He said \"goodbye\" and left";

    let text = r#"He said "goodbye" and left"#; // raw string literal (1)
    let re = regex::Regex::new(r#"\b(word)\b"#).unwrap();
    ```

    1. Raw string literals can be useful in cases like writing regular expressions or defining JSON objects as string literals.

2. Byte string: are created by prefixing a string literal with a `b`. This creates a slice of bytes which is useful for dealing with network protocols that expects a byte sequence.

```rust
let http_ok: &[u8; 17] = b"HTTP/1.1 200 ok\r\n";
```

### `&mut str`
String slices are usually represented as `&str`, i.e, immutable. But it is possible to create a mutable reference, i.e., `&mut str`.

This allows us to directly modify the contents of a string slice while ensuring memory safety and UTF-8 compliance.

<mark class="y">Useful for in-place string transformations without needing to create a allocate memory for separate string.</mark>

```rust
fn anonymize_emails(s: &mut str) {
    let re = regex::Regex::new(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b").unwrap();

    let mut matches = Vec::new();

    // ..

    // Now that we have the matches, perform the replacements
    let s_bytes: &mut [u8] = unsafe { s.as_bytes_mut() };
    for range in matches {
        let replacement = vec![b'*'; range.end - range.start];
        s_bytes[range].copy_from_slice(&replacement);
    }
}
```

!!! warning

    Mutable slices are generally avoided in idiomatic Rust code due to complexities and potential of invalid UTF-8 string.

### `Cow<'a, str>`
`Cow` or *Copy on write*, is useful when you have a function that sometimes modifies a string and other times doesn't, and you want to avoid making new allocation in cases where no modifications are made.


```rust
use std::borrow::Cow;

fn sanitize(input: &str) -> Cow(str) {
    if input.contains("badword") {
        let sanitized: String = input.replace("badword", "****");
        return Cow::Owned(sanitized);
    }
    Cow::Borrowed(input)  // (1)
}
```

1. Returns the string withuot allocating anything a new string

---
Let's discuss string types that focuses on interoperability, which abstract away differences between operating systems and help Rust code connect with other languages.

### `OsString` & `OsStr`
`OsString` & `OsStr` can contain any sequence of bytes on unix-like systems or
any sequence of 16-bit values on Windows. This is useful for interacting with system calls that don't require strings to be UTF-8 encoded.

```rust
fn main() -> std::io::Result<()> {
    let paths = fs::read_dir(".")?;

    for path in paths {
        match path {
            Ok(entry) => {
                let os_string: OsString = entry.file_name();
                match os_string.into_string() {
                    Ok(string) => println!("Found a file: {]", string),
                    Err(os_string) => println!("Found a non-UTF-8 filename: {:?}", os_string),
                }
            }
            Err(_) => println!("Couldn't read the path."),
        }
    }

    Ok(())
}
```

### `Path` & `PathBuf`
`Path` is an immutable view of a path, useful for reading or inspecting paths.

`PathBuf` is a mutable and owned version of `Path` similar to `String` type, used when you want to create or modify paths.

These are useful for filesystem handling across various OSs, as they handle file paths differently.

Let's see an example:

```rust
fn read_file(dir: &Path, filename: &str) -> std::io::Result<String> {
    let mut full_path = PathBuf::from(dir);
    full_path.push(filename);

    let mut file = File::open(full_path)?;
    let mut content = String::new();
    file.read_to_string(&mut content)?;

    Ok(content)
}

fn main() -> std::io::Result<()> {
    let dir = Path::new("./");
    let content = read_file(dir, "example.txt")?;
    println!("File content: {}", content);

    Ok(())
}
```

### `CStr` & `CString`
Useful when interfacing rust code with C libraries that expects null terminated strings, providing a safe way to handle C compatible strings.

Let's see an example of retrieving env variable from a C code:

```rust
extern "C" {
    fn getenv(name: *const str::os::raw::c_char) -> *const std::os::raw::c_char;
}

use std::ffi::{CStr, CString};

fn main() {
    let key = CString::new("PATH").expect("CString::new failed");
    unsafe {
        let val = getenv(key.as_ptr());
        if val.is_null() {
            let c_str = CStr::from_ptr(val);
            let str_slices = c_str.to_str().unwrap();
            println!("Found: {}", str_slice
        } else {
            println!("Not found");
        }
    }
}
```
