# Quack

# Running
Many bash scripts are provided. `quack` will compile and execute, and `quackc` will compile but not execute a given program. Additionally, `compile` will compile a .qk file to .asm, `assemble` will assemble it into object code, and `run` will run an assembled program. 

Scripts will produce a .asm file with the same name as the input .qk file containing a single class of the same name, so long as additional classes are not defined. (For example, `./quack qk_test/If.qk` will compile If.asm and run If.json in the tiny_vm). 

If the file contains multiple class definitions (such as the sample `ReturnCheck`), a separate .asm file will be created with the name of each class, as well as a class containing [TODO]

For example, to run `ReturnCheck.qk`, the sequence would be
```
./compile ReturnCheck.qk
./assemble Test.asm
./assemble ReturnCheck.asm
./run ReturnCheck
```
`Class.qk` is the other 

A number of tests are given in the directory `tests/`. Bad test files follow the naming convention `bad_xxxx.qk`, and demonstrate a program error that the quack compiler will catch. The specific compiler error might seem a bit weird but the point it that it won't work. This can be tested with either `compile` or `quack[c]`, since the error is in the compilation step. The test files are all named for the feature that they demonstrate.

It is possible that you will need to re-compile the tiny vm. This can be done by running the following commands, in-order.
```
cd vm
cmake -Bcmake-build-debug -S.
cd cmake-build-debug
make
```

# Things that work
## Parsing
All major features of Quack except one work in the test cases I have provided (see later for elaboration).

## Type-checking
Declared variables, fields, assignments, method arguments, calls and return values from calls, method calls on objects.

# Things that don't work (or sort of don't work)

`x.y.z` - only one field access parses correctly. I know why this is a problem but it would be likely very difficult/annoying to fix.

Uninitialized variables - these will throw an error, but the error isn't that it's uninitilized. Rather, new variables all get type NOTHING, and the error is thrown on a type check. 

Short strings ("...") - Certain \c characters are meant to be illegal - they are allowed. I had many issues with the regex for this and eventually decided that making other things work (classes, type checking, etc.) was higher priority. 

# Notes
I admitted defeat for certain aspects of this compiler, slightly because of time purposes (I am in Wisconsin for Nationals and had less time than I anticipated to work) but mainly because I made some structural choices early on that I didn't realize would be problems until I attempted some of the harder aspects such as flow-sensitive analysis, and fixing these issues would require basically rewriting everything. This made it difficult to properly implement certain features like flow-sensitive analysis and static typing for variables. 

I also kept running into small errors due to these structural decisions, and I wasn't able to test the system as extensively as I would have liked. 