# Deterministic Pushdown Automata

This is an general implementation of deterministic pushdown automata in Python.
The DPDA base class is designed such that it is easy to derive any DPDA by defining the rule set.

I created this for the class "Theory of Computation" in Fall 2024.



### Examples


#### `L = { a^nb^n | n >= 1 }`

```
$ main.py '$'
Processing $
┌─────────────────────────────────────┬──────────────────┐
│        DPDA Processing State        │    Rules used    │
├──────┬───────┬──────────────┬───────┼───────┬──────────┤
│ Step │ State │ Unread input │ Stack │ Delta │ R        │
├──────┼───────┼──────────────┼───────┼───────┼──────────┤
│    0 │ p     │ $            │     e │       │          │
│    1 │ q     │ $            │     S │     1 │          │
│    2 │ q$    │ e            │     S │     6 │          │
└──────┴───────┴──────────────┴───────┴───────┴──────────┘
Success

$ main.py 'ab$'
Processing ab$
┌─────────────────────────────────────┬──────────────────┐
│        DPDA Processing State        │    Rules used    │
├──────┬───────┬──────────────┬───────┼───────┬──────────┤
│ Step │ State │ Unread input │ Stack │ Delta │ R        │
├──────┼───────┼──────────────┼───────┼───────┼──────────┤
│    0 │ p     │ ab$          │     e │       │          │
│    1 │ q     │ ab$          │     S │     1 │          │
│    2 │ qa    │ b$           │     S │     2 │          │
│    3 │ qa    │ b$           │   aSb │     7 │ S -> aSb │
│    4 │ q     │ b$           │    Sb │     3 │          │
│    5 │ qb    │ $            │    Sb │     4 │          │
│    6 │ qb    │ $            │     b │     8 │ S -> e   │
│    7 │ q     │ $            │     e │     5 │          │
│    8 │ q$    │ e            │     e │     6 │          │
└──────┴───────┴──────────────┴───────┴───────┴──────────┘
Success

$ main.py 'aabb$'
Processing aabb$
┌─────────────────────────────────────┬──────────────────┐
│        DPDA Processing State        │    Rules used    │
├──────┬───────┬──────────────┬───────┼───────┬──────────┤
│ Step │ State │ Unread input │ Stack │ Delta │ R        │
├──────┼───────┼──────────────┼───────┼───────┼──────────┤
│    0 │ p     │ aabb$        │     e │       │          │
│    1 │ q     │ aabb$        │     S │     1 │          │
│    2 │ qa    │ abb$         │     S │     2 │          │
│    3 │ qa    │ abb$         │   aSb │     7 │ S -> aSb │
│    4 │ q     │ abb$         │    Sb │     3 │          │
│    5 │ qa    │ bb$          │    Sb │     2 │          │
│    6 │ qa    │ bb$          │  aSbb │     7 │ S -> aSb │
│    7 │ q     │ bb$          │   Sbb │     3 │          │
│    8 │ qb    │ b$           │   Sbb │     4 │          │
│    9 │ qb    │ b$           │    bb │     8 │ S -> e   │
│   10 │ q     │ b$           │     b │     5 │          │
│   11 │ qb    │ $            │     b │     4 │          │
│   12 │ q     │ $            │     e │     5 │          │
│   13 │ q$    │ e            │     e │     6 │          │
└──────┴───────┴──────────────┴───────┴───────┴──────────┘
Success

$ main.py 'aaabbb$'
Processing aaabbb$
┌─────────────────────────────────────┬──────────────────┐
│        DPDA Processing State        │    Rules used    │
├──────┬───────┬──────────────┬───────┼───────┬──────────┤
│ Step │ State │ Unread input │ Stack │ Delta │ R        │
├──────┼───────┼──────────────┼───────┼───────┼──────────┤
│    0 │ p     │ aaabbb$      │     e │       │          │
│    1 │ q     │ aaabbb$      │     S │     1 │          │
│    2 │ qa    │ aabbb$       │     S │     2 │          │
│    3 │ qa    │ aabbb$       │   aSb │     7 │ S -> aSb │
│    4 │ q     │ aabbb$       │    Sb │     3 │          │
│    5 │ qa    │ abbb$        │    Sb │     2 │          │
│    6 │ qa    │ abbb$        │  aSbb │     7 │ S -> aSb │
│    7 │ q     │ abbb$        │   Sbb │     3 │          │
│    8 │ qa    │ bbb$         │   Sbb │     2 │          │
│    9 │ qa    │ bbb$         │ aSbbb │     7 │ S -> aSb │
│   10 │ q     │ bbb$         │  Sbbb │     3 │          │
│   11 │ qb    │ bb$          │  Sbbb │     4 │          │
│   12 │ qb    │ bb$          │   bbb │     8 │ S -> e   │
│   13 │ q     │ bb$          │    bb │     5 │          │
│   14 │ qb    │ b$           │    bb │     4 │          │
│   15 │ q     │ b$           │     b │     5 │          │
│   16 │ qb    │ $            │     b │     4 │          │
│   17 │ q     │ $            │     e │     5 │          │
│   18 │ q$    │ e            │     e │     6 │          │
└──────┴───────┴──────────────┴───────┴───────┴──────────┘
Success
```
