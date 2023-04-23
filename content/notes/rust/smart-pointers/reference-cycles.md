# Smart Pointers in Rust - References Cycles


!!! danger

    Rust is known for memory safety so it guarantees you can't have data races, but it doesn't provide you the same guarantee for memory leaks.

We can have memory leak issues with `Rc<T>` smart pointer or `RefCell<T>` smart pointer. **In both we can have items that reference each other in a cycle which leads to memory leaks.**

[Reference Cycles Can Leak Memory](https://doc.rust-lang.org/stable/book/ch15-06-reference-cycles.html){ .md-button }

Let's learn by an example:

## Creating a Reference Cycle

```rust
use crate::List::{Cons, Nil};
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
enum List {
    Cons(i32, RefCell<Rc<List>>),
    Nil,
}

impl List {
    fn tail(&self) -> Option<&RefCell<Rc<List>>> {
        match self {
            Cons(_, item) => Some(item),  // get list from `Cons` variant if it is `Cons`
            Nil => None,                  // otherwise Nil
        }
    }
}

fn main() {
    // Create Reference Cycle
    // Wrapped in `Rc<T>` to have multiple owners
    let a = Rc::new(Cons(5, RefCell::new(Rc::new(Nil))));

    println!("a initial rc count = {}", Rc::strong_count(&a)); // should be 1
    println!("a next item = {:?}", a.tail());   // next will be `Nil`

    // create b which stores 10 next item being `a`
    let b = Rc::new(Cons(10, RefCell::new(Rc::clone(&a))));

    println!("a rc count after b creation = {}", Rc::strong_count(&a)); // should be 2
    println!("b initial rc count = {}", Rc::strong_count(&b));  // should be 1
    println!("b next item = {:?}", b.tail());

    // modifying list `a` to store list `b`
    if let Some(link) = a.tail() {
        // `link` will be wrapped in `Rc<T>`
        // so get mutable reference to `link`'s data
        // and change it to Reference to `b`.
        *link.borrow_mut() = Rc::clone(&b);
    }

    // print reference counts of `b` and `a`.
    println!("b rc count after changing a = {}", Rc::strong_count(&b));  // should be 2
    println!("a rc count after changing a = {}", Rc::strong_count(&a));  // should be 2

    // Uncomment the next line to see that we have a cycle;
    // it will overflow the stack
    // println!("a next item = {:?}", a.tail());
}
```

Running this outputs:

```text
a initial rc count = 1
a next item = Some(RefCell { value: Nil })
a rc count after b creation = 2
b initial rc count = 1
b next item = Some(RefCell { value: Cons(5, RefCell { value: Nil }) })
b rc count after changing a = 2
a rc count after changing a = 2
```

**We just created a Reference cycle.**

![](/assets/images/notes/rust/reference_cycles_0.png)

On stack there are two pointers `a` and `b` which points to some memory stored on Heap called `'a` & `'b`. `'a` holds integer 5 and value `Nil`. Similarly `'b` stores integer 10 and then a reference to `'a`. So, the reference count for `a` is 2.

Then we modified list `a` to store a reference of `b` (line number 40):

![](/assets/images/notes/rust/reference_cycles_1.png)

That means for `b` as well we'll have reference count of 2.

If we uncomment the last `println!()` line (line 49) we'll get stack overflow. If we print next item of `a` which will be `b` then we print next item of `b` which is `a` and this goes on infinitely.

<mark class="v">This circular dependency causes memory leaks, because at the end of `main()`, `a` and `b` should be cleaned up</mark>. First `b` will be cleaned up (remember, variables goes out of scope in reverse order) from stack, but the memory location it point to on heap will still exist because that is still being referenced inside `a`. Then `a` will be cleaned up from stack but memory on heap will not be cleaned for the same reason.

![](/assets/images/notes/rust/reference_cycles_2.png)

So, to list exists on heap but no variables on stack references them on stack. Leading to memory leak.

So, Reference cycles are difficult to create but they are not impossible to create.

So far we only had to deal with the pointers that own the data they point, but if we are in the situation where it's okay to get away with pointers that don't own the data they point to, i.e., **Weak pointers**, then we can also prevent Reference cycles.

## Creating a Tree Data Structure

```rust
use std::cell::RefCell;
use std::rc::Rc;

#[derive(Debug)]
struct Node {
    value: i32,
    // children of a Node is a Vector of Node wrapped
    // in `Rc<T>` so that variables outside of this tree to be able to point
    // to node so we can traverse
    // Wrapped in `RefCell<T>` to modify a node's children
    children: RefCell<Vec<Rc<Node>>>,
}

fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]), // empty vec
    });

    let branch = Rc::new(Node {
        value: 5,
        // branch stores the `leaf` as children
        children: RefCell::new(vec![Rc::clone(&leaf)]),
    });
}
```

We can't get to `branch` node from `leaf` node because children don't know about parent; so we'll need parent references.

## Weak Smart pointer | Adding Reference from Child to it's Parent
!!! info

    The `Weak` smart pointer is a version of `Rc` that <mark class="y">hold a non-owning reference to the managed allocation.</mark>

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};  // import `Weak<T>`

#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,
    // `RefCell<T>` to modify the parent node
    // variables outside of tree to be able to reference the parent,
    // so we want parent node to have multiple ownership.
    // BUT, `Rc<Node>` will create Reference Cycle.
    // Luckily we don't need that; childrens don't own the parent.
    // when children goes out of scope, parent remains.
    // This is where `Weak<T>` smart pointer come into play
    parent: RefCell<Weak<Node>>
}


fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        children: RefCell::new(vec![]),
        // construct new `Weak<T>` without allocating any memory
        parent: RefCell::new(Weak::new()),
    });

    // `upgrade()` attempts to upgrade `Weak<T>` pointer to `Rc<T>`
    // returns a option, because underlying valye may have dropped.
    // We do this because `Weak<T>` has no idea if the inner valye is dropped or not.
    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());

    let branch = Rc::new(Node {
        value: 5,
        children: RefCell::new(vec![Rc::clone(&leaf)]),
        parent: RefCell::new(Weak::new()),
    });

    // modify `leaf`'s node to store branch node's reference as parent
    // get mutable reference using `borrow_mut()` and then using dereference operator
    // `*` to change the value to `branch` node
    // `branch` is a reference counting smart pointer; while our `parent` field expects
    // `Weak<T>`. To make the convertion happen we call `Rc::downgrade()`
    *leaf.parent.borrow_mut()= Rc::downgrade(&branch);

    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());
}
```

Running this outputs:

```text
leaf parent = None
leaf parent = Some(Node { value: 5, children: RefCell { value: [Node { value: 3, children: RefCell { value: [] }, parent: RefCell { value: (Weak) } }] }, parent: RefCell { value: (Weak) } })
```

## strong_count vs weak_count
Internally `Rc<T>` stores two counts, `weak_count` and a `strong_count`.

1. **Strong Count**: the number of references which have ownership of the data.
2. **Weak Count**: the number of references which don't have the ownership of the data.

```rust
use std::cell::RefCell;
use std::rc::{Rc, Weak};  // import `Weak<T>`

#[derive(Debug)]
struct Node {
    value: i32,
    children: RefCell<Vec<Rc<Node>>>,
    parent: RefCell<Weak<Node>>
}

fn main() {
    let leaf = Rc::new(Node {
        value: 3,
        parent: RefCell::new(Weak::new()),
        children: RefCell::new(vec![]),
    });

    println!(
        "leaf strong = {}, weak = {}",
        Rc::strong_count(&leaf),
        Rc::weak_count(&leaf)
    );

    {
        let branch = Rc::new(Node {
            value: 5,
            parent: RefCell::new(Weak::new()),
            children: RefCell::new(vec![Rc::clone(&leaf)]),
        });

        // modify `leaf` node's parent field to be a weak reference to branch node
        *leaf.parent.borrow_mut() = Rc::downgrade(&branch);

        println!("\nInside inner scope");
        println!(
            "branch strong = {}, weak = {}",
            Rc::strong_count(&branch),
            Rc::weak_count(&branch)
        );

        println!(
            "leaf strong = {}, weak = {}",
            Rc::strong_count(&leaf),
            Rc::weak_count(&leaf)
        );
    }

    // after the inner scope ends the branch node will have
    // strong count of 0 and will be dropped
    // Branch node still has weak count of 1 because
    // leaf has weak reference to branch however that doesn't affect
    // if the underlying value is dropped or not

    println!("\nOutside inner scope");
    println!("leaf parent = {:?}", leaf.parent.borrow().upgrade());
    println!(
        "leaf strong = {}, weak = {}",
        Rc::strong_count(&leaf),
        Rc::weak_count(&leaf)
    );
}
```

Running this outputs:

```text
leaf strong = 1, weak = 0

Inside inner scope
branch strong = 1, weak = 1
leaf strong = 2, weak = 0

Outside inner scope
leaf parent = None
leaf strong = 1, weak = 0
```
