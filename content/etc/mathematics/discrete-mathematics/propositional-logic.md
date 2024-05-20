# Propositional Logic

Content inspired from:
<iframe width="999" height="400" src="https://www.youtube.com/embed/5NGKbiA04Cw" title="An Introduction to Propositional Logic" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Computer Scientists use formal logical systems for expressing ideas about statements and whether they are true.

Propositional logic stems from the word "propositions", <mark class="y"> sentences that can be either true or false.</mark >

We'll often use a variable to stand for the proposition, like:

$$
P: \text{The robot is blue}
$$

Now this proposition can be true/false depending on the current state of the world.

- $P$ holds true if robot is blue.
- $P$ is false if robot is _not_ blue.

## Truth Table

Truth table can display all of the possible combinations of the values for variables in a certain propositional logic and show if the formula holds true or false.

## Modifying a logical formula

### Negation ($\neg$)

So, to convey the statement, $P$ is not true, i.e., _"The robot is blue"_ _does not_ hold true we use this symbol $\neg$

$$
\neg P: \text{The robot is not blue}
$$

### Conjunction ($\land$)

This expresses, **both** statement holds true.

$$
P: \text{The robot is blue}\newline
Q: \text{The robot has antenna}
$$

Then conjunction ($P \land Q$) holds true <mark class="y">when the robot is **both** blue and has antenna as well.</mark>

So, we can visualize this with truth table as:

| $P$                                 | $Q$                                 | $P \land Q$                         |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  |

### Disjunction ($\lor$)

This expresses, **at least** one of them is true.

So, disjunction ($P \lor Q$) holds true when <mark class="y">**either** the robot is blue or has antenna or **both**</mark>.

We can visualize this with truth table as:

| $P$                                 | $Q$                                 | $P \lor Q$                          |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  |

### Exclusive Or ($\oplus$)

$P \oplus Q$ expresses, <mark class="y">$P$ is true **or** $Q$ is true **but not both**.</mark>

| $P$                                 | $Q$                                 | $P \oplus Q$                          |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ |

### Implication ($\implies$)

If propositions are:

$$
P: \text{The robot is blue}\newline
Q: \text{The robot has antenna}
$$

<div class="annotate" markdown>
then, $P \implies Q$ (1), tells </mark class="y">if the robot is blue, then it also must be true that the robot has antenna</mark>. 
</div>

1. Read as *$P$ implies $Q$ or *if $P$ then $Q$\*.

$$
P \implies Q:
$$

<div class="annotate" markdown>
| $P$                                 | $Q$                                 | $P \implies Q$                         |
| ----------------------------------- | ----------------------------------- | -------------------------------------- |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$ (1) |  
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$ (2) |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$    |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$     |
</div>

1. The formula doesn't state when $P$ is _not true_, it's assumed maybe the robot has antenna, maybe it doesn't.
2. The formula doesn't state when $P$ is _not true_, it's assumed maybe the robot has antenna, maybe it doesn't.

!!! info

    Imagine you said something like, *"If it's my birthday, then I'll eat cake"*.

    If it's your birthday, then as per statemtn you'll eat a cake, but it's doesn't mean that you may or may not eat a cake, if it's not your birthday.

This logic can be also be said as $\neg P \lor Q$. i.e., robot is not blue or robot has an antenna.

### Biconditional ($\iff$)

This expresses, read as _"if and only if"_.

- If $P$ is true, then $Q$ is true
- If $P$ is false, then $Q$ is false.

| $P$                                 | $Q$                                 | $P \iff Q$                      |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  |
| $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#f56c42}{\text{false}}$ | $\textcolor{#f56c42}{\text{false}}$ |
| $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  | $\textcolor{#07fc03}{\text{true}}$  |

