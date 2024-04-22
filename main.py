import re
import os

ASM_FILE = "test.asm"

# nodes types for Nano-quack
STRING, INT, OBJ, BOOLEAN, NOTHING = range(5)

class Obj():
    def __init__(self, value: None):
        self.val = value
        self.type = OBJ

    def get_type(self) -> int:
        return self.type

    def evaluate(self):
        return self

class Int(Obj):
    def __init__(self, value: int):
        self.val = value
        self.type = INT

class String(Obj):
    def __init__(self, value: str):
        self.val = value
        self.type = STRING

class Bool(Obj):
    def __init__(self, value: bool):
        self.val = value
        self.type = BOOLEAN

class Nothing(Obj):
    def __init__(self):
        self.val = None
        self.type = NOTHING

class Variable(Obj):
    vars = {}

    def __init__(self, name: str, value: Obj):
        self.name = name
        self.value = value
        self.type = value.get_type()

        Variable.vars[self.name] = self.type

    def get_type(self) -> int:
        return self.type
    
    def evaluate(self) -> Obj:
        return self.value

class Operator():
    # operator tree
    ops = {"+": "plus", "-": "minus", "*": "times", "/": "divide"}

    def __init__(self, left: Obj, right: Obj, op: str):
        self.left = left
        self.right = right
        if op in "+-*/":
            self.op = Operator.ops[op]
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")

    def evaluate(self):
        a = self.left.evaluate()
        b = self.right.evaluate()

        # print to file
        pass

"""
grammar

assign = '
start -> var: [type] = sum;

sum -> prod + prod (add)
sum -> prod - prod (minus)

prod -> prod * prod (times)
prod -> prod / prod (divide)
prod -> num
'
"""

def parse(expr: str) -> Obj:
    pass

def evaluate(typ: str, expr: str) -> Obj:
    eval = parse(expr)
    pass

def main():
    try:
        open(ASM_FILE, "x")
    except FileExistsError:
        os.remove(ASM_FILE)

    # write header information
    f = open(ASM_FILE, "a")
    print(".class Calculator:Obj", file=f)
    print(".method $constructor", file=f)
    print("\tenter", file=f)

    f.close()

    quack = []

    assignment = r"\w+:"
    var_type = r"Int|Bool|String|Obj"
    expr = r"\= \-?.+([-+*/]\-?.+)*;"

    # read quack
    with open("ex.qk", "r") as qk:
        lines = qk.readlines()
        for line in lines:
            if (line == "\n"):
                continue
            temp = []
            temp.append(re.match(assignment, line).group().strip(":"))
            temp.append(re.search(var_type, line).group())
            temp.append(re.search(expr, line).group().strip("=;"))
            quack.append(temp)

    # build tree
    # print(quack)

    for line in quack:
        expr = evaluate(line[1], line[2])
        var = Variable(line[0], expr)

    f = open(ASM_FILE, "a")
    print("\treturn 0", file=f)
    f.close()

if __name__ == "__main__":
    main()


