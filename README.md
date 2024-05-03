# Quack

# Instructions
Run
```
python parse.py <filename>.qk
```
to parse the input file to assembly. The default output file is `Main.asm`. There is a sample file provided called `ex.qk`; running the program with no additional arguments will parse that default file. It contains a number of legitimate assignments followed by a number of horribly wrong assignments. Good luck!

As instructed, there is no error checking. You can enter things such as `5abc`. What will the parser do? Nobody knows. You can also have fun lines such as `5 + "Hi" - False;`. This will certainly not run, but it will parse just fine. 

Test files should follow the syntax of ex.qk - that is, assignments and absolutely nothing else. I cannot promise that trying to be fancy ("correct") will not break the parser altogether. 

## Part 2 - Mini-Quack
Mini-quack is as much of Quack as we can get in a single method --- including control structures and type inference. 

In this project, please provide a top-level README with complete build instructions. 

Also provide a shell (bash) script called "quack" that ties together all the steps to compile and run a quack program.  If I type "quack ../MyTestCase.qk", I would like it to produce the assembly code, assemble it into a file in the OBJ directory, and then invoke the vm to run it.    I suggest but will not insist on also creating a script "quackc" that does all but the last step, i.e., it creates the OBJ/something.json file but does not execute it.   

In Mini-Quack, type declarations are optional.   If we assign x = 7 + y, and y is an integer, then we will infer that x is an integer.  If x is assigned an integer value on one path through the method, and assigned a string value on another path through the method, then we will infer that the type of x is Obj  (the most specific class that could be either an integer or a string).  If we infer the type of x is Obj, but we see z = x + 7, then we will report a type error because Obj does not have a PLUS method. 

There are a few features of Quack that we can't include until we have user-written classes and methods.  One of these is access to fields (e.g., x.f1 = y.z.f2), because none of the built-in types have accessible fields (also known as "instance variables").  I will also put off implementation of "typecase" statements for the next sprint. 

Type inference in Quack is flow-insensitive:  We infer a single type for a variable throughout the whole method.  In other words, type inference does not depend on which path program execution follows through the control flow.  We will also have a flow-sensitive static analysis, which we will use to ensure that variables are initialized before they are used.   Flow sensitive analysis considers the potential state of a variable at each point in the program text (e.g., within a particular branch of an if statement).   We distinguish flow-sensitive (what state could x be in here?) from path-sensitive (what state could x be in given how I got here?).  For example, we will have only one summary state for x at a certain point in a loop, regardless of whether it is the first time through the loop or a subsequent time.    What we think of as "compilers" are typically scripts that tie together individual tools like this.  The Python interpreter works like the 'quack' script, and gcc, cc, clang etc. work like quackc, as does javac.  

Please turn in a your github URL with your assignment three work merged into the main branch, then start a new branch for the following project, so that I can simply clone the main branch of your repository for grading.  