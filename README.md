# Quack

# Running
Two bash scripts are provided. `quack` will compile and execute, and `quackc` will compile but not execute a given program.

Both script will produce a .asm file with the same name as the input .qk file containing a single class of the same name. (For example, `./quack qk_test/If.qk` will compile If.asm and run If.json in the tiny_vm).

Some tests are given in the directory `qk_test/`. Bad test files follow the naming convention `Bad_xxxx.qk`, and demonstrate a program error that the quack compiler will catch.

It is possible, but unlikely, that you will need to re-compile the tiny vm. This can be done by running the following commands, in-order.
```
cd vm
cmake -Bcmake-build-debug -S.
cd cmake-build-debug
make
```

# What does the compiler do at this point?
## Parsing
Currently, `quack.py` compiles a sequence of statements, including variables. Control flow and integer comparison operations (<, >, ==) are implemented, however boolean comparisons `and`, `or` are not 100% correct. They parse correctly and are added to the AST, however the assembly instructions are wrong because I wasn't sure what it was supposed to look like.

Method calls are also allowed on built-in variables, specifically print. I would be wary of trying anything else because only print has been rigorously tested. 

## Type-checking
Type checking is implemented for declared variables, arithmetic expressions, and conditional statements. For declared variables, a declared type overrides assignment. Binary operators must have the same type for both operands, regardless of what that type is, and conditional statements must be Boolean values. 

## Flow-sensitive analysis
I have not gotten here yet. 

# Note
I'm not sure where we were supposed to be by this assignment but I'm pretty sure I'm not all the way there. I'm still working on it and am not too worried about getting everything functional by the end of the term/final due date for the project at this point. 

I just wanted to make sure I submitted something to show my progress by the end of the weekend for this, so here's where I'm at.