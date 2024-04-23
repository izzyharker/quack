# Quack

# Instructions
Run
```
python parse.py <filename>.qk
```
to parse the input file to assembly. The default output is "[filename].asm". There is a sample file provided called `ex.qk`, running the program with no additional arguments will parse that default file. 

As instructed, there is no error checking. You can enter things such as `5abc`. What will the parser do? Nobody knows. You can also have fun lines such as `5 + "Hi" - False;`. This will certainly not run, but it will compile just fine. 

## Part 1
In our second "sprint", we will translate a basic subset of the Quack language:  A sequence of assignment statements, including method calls on the built-in classes.  We will not create new classes or methods, but we will consider the sequence of assignment statements we create the body of a constructor for a special "Main" class (which we may give another name like "$Main" so that it can't conflict with any class a user could write).  

We will not include control flow (no if statements, no while statements) in this subset of Quack. 

For this subset, we will require each assignment to include a type declaration, like this: 

x: Int = 13 + y; 

Most of these type declarations will be optional in full Quack, but we are holding off on type inference until we get farther in the project.  We are also holding off on most other static checking.  It is up to the user to give us correct programs.  (In contrast, production compilers put a lot of effort into preventing certain kinds of errors, like type mismatches).   If the user program contains this statement: 

x: Int = "Why would you " + "do this?" - 3; 

we will translate it without complaint.  It will probably cause car crashes, house fires, and seg faults, but nano-quack has no protections against any of that. 

Even with only a sequence of assignment statements and no error checking, this is a substantial project.  You will need to write grammar for a good deal of Quack (I'll help).  You will need to keep track of local variables and their types.  You will need to "de-sugar" the algebraic notation into calls on methods (much like "magic methods" in Python).   

Do not try to tackle this all at once.  Start really small ... even smaller than Nano-quack.  Start with Pico-quack and build up.  What exactly should be in Pico-quack?  Maybe just assignments to integer variables, with each variable being assigned to exactly once?   Maybe with just addition and subtraction?   The smaller you start, the easier your debugging will be, and the better you will be able to think through the problems you are solving. 

For this project, a high degree of collaboration is permitted and encouraged.  It is ok to work together, but you must turn in your own code, and you must understand every line of the code you turn in.   Also you must document the collaboration in comments.  