# Quack

# Running
Many bash scripts are provided. `quack` will compile and execute, and `quackc` will compile but not execute a given program. Additionally, `compile` will compile a .qk file to .asm, `assemble` will assemble it into object code, and `run` will run an assembled program. 

Scripts will produce a .asm file with the same name as the input .qk file containing a single class of the same name, so long as additional classes are not defined. (For example, `./quack qk_test/If.qk` will compile If.asm and run If.json in the tiny_vm). If additional classes are defined, each will get its own .asm file with the name of the file matching the name of the class. In the case that a user-defined class shares a name with the original file (`Ex.qk` containing `class Ex()`), the statements at the end will be moved to `Main.asm`. Please don't name a class `Main`, it will probably break something and I would be sad. 

For example, to run `ReturnCheck.qk`, the sequence would be
```
./compile ReturnCheck.qk
./assemble Test.asm
./assemble ReturnCheck.asm
./run ReturnCheck
```
`Class.qk` is the other 

A number of tests are given in the directory `tests/`. Bad test files follow the naming convention `bad_xxxx.qk`, and demonstrate a program error that the quack compiler will catch. This can be tested with either `compile` or `quack[c]`, since the error is in the compilation step. In general, the name of the test file describes the feature that it demonstrates success or error catching on. 

It is possible that you will need to re-compile the tiny vm. This can be done by running the following commands, in-order.
```
cd vm
cmake -Bcmake-build-debug -S.
cd cmake-build-debug
make
```

`quack.py` contains all the parsing and tree generation functionality, as well as the main execution function. `AST.py` contains the `ASTNode` class implementation and all the tree evaluation/type checking functionality. Each ASTNode (for the most part) has a `check` method, which does the necessary type checking for each node, and an `evaluate` method, which generates the asm code. 

# Things that work
The features described here all work, along with all other features of Quack, except those described in "Things that don't work" (below). It is possible that there are some edge cases I didn't manage to check, but I have a pretty comprehensive suite of good/bad tests that run (or don't run, depending).  

If you would like the most involved example of all the things that work, `tests/Pt.qk` is the sample `Pt` program, with some added statements to test the class functionality. It runs correctly. 
 
 ## Type-checking
 Type-checking is flow-sensitive for the most part. Normal variables can be re-assigned to different types, with 2 exceptions.
 - Fields cannot be reassigned once they are given a type, either explicitly or implicitly
 - If a variable is given an explicit type (such as `x: Int`), then the variable cannot be assigned a different type within that particular assignment. For example, 
```
x: Int = "hi";
```
is illegal, but
```
x: Int = 7;
x = "hi";
```
is allowed. 

## Classes
Class definition follows as normal. Assembling classes is a bit tricky because they are split into separate files. 
- If the file name matches a declared class and the file contains statements at the end, then the statements will be put into a `Main.asm` file and the declared classes will be under matching filenames (class Class -> Class.asm). Otherwise, the statements will go under filename.asm. 
- Suggested compilation steps for files with user-defined classes:
```
./compile [file].qk
foreach user-defined class in file U:
    ./assemble [U].asm
./assemble [Main or file].asm
./run [Main or file]
```

# Things that don't work
## Flow-sensitive variable scope
This slipped my mind until right at the very end, and I did not have time to implement it. Currently, every variable declared in any if/elif/else block will count as initialized, whether it actually exists _in the code_ or not. That is,
```
if (x) {
    y = 1;
}
else {
    z = 1;
}
y.print();
```
will run, even though it should complain.

## not [bool]
I wrote not to work with the comparison and and/or operator and forgot about it. Consequently, `not true` and things like that don't work. Whoops.