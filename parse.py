import re
import os
import sys
import logging as log

log.basicConfig(level=log.INFO)

# nodes types for Nano-quack
OBJ, INT, NEGINT, STRING, BOOL, NOTHING = range(6)

node_types = {OBJ: "OBJ", INT: "INT", NEGINT: "NEGINT", STRING: "STRING", BOOL: "BOOL", NOTHING: "NOTHING"}

class Obj():
    ASM_FILE = "out.asm"

    def __init__(self, value: None):
        self.val = value
        self.type = OBJ

    def get_type(self) -> int:
        return self.type

    def evaluate(self):
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tconst {self.val}", file=f)
        f.close()
        # print(f"\tconst {self.val}")
    
    def __str__(self):
        return f"({node_types[self.type]}, {self.val})"

class Int(Obj):
    def __init__(self, value: int):
        super().__init__(value)
        self.val = value
        self.type = INT

class NegInt(Obj):
    def __init__(self, value: int):
        super().__init__(value)
        self.val = abs(value)
        self.type = INT

class String(Obj):
    def __init__(self, value: str):
        super().__init__(value)
        self.val = value
        self.type = STRING

class Bool(Obj):
    def __init__(self, value: bool):
        super().__init__(value)
        self.val = value
        self.type = BOOL

class Nothing(Obj):
    def __init__(self):
        super().__init__(None)
        self.val = None
        self.type = NOTHING

class Variable(Obj):
    vars: dict[str: Obj] = {}

    def __init__(self, name: str, value: Obj):
        self.name = name
        self.val = value
        self.type = OBJ

        Variable.vars[self.name] = self

    def get_type(self) -> int:
        return self.type
    
    def evaluate(self) -> Obj:
        self.val.evaluate()
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tstore {self.name}", file=f)
        f.close()

class Operator(Obj):
    # operator tree
    ops = {"+": "plus", "-": "minus", "*": "times", "/": "divide"}

    def __init__(self, left: Obj, right: Obj, op: str):
        self.left = left
        self.right = right
        if op in "+-*/":
            self.token = op
            self.op = Operator.ops[op]
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")

    def evaluate(self):
        self.left.evaluate()
        self.right.evaluate()

        # print to file
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tcall Int:{self.op}", file=f)
        f.close()
        # print(f"\tcall Int:{Operator.ops[self.op]}")
        
        pass

    def __str__(self):
        return f"({self.left} {self.token} {self.right})"

"""
grammar

assign = '
start -> var: [type] = sum;

sum -> sum + prod (add)
sum -> sum - prod (minus)

prod -> prod * prod (times)
prod -> prod / prod (divide)
prod -> num
'
"""

class Tree():
    types = {"NegInt": r"-\d+", "Int": r"\d+", "String": r"\".*\"", "Bool": r"True|False", "LParen": r"\(.*\)?", "RParen": r"\(?.*\)"}

    def __init__(self, expr: list[str]):
        self.index = 0
        self.tokens = expr
        self.num_tokens = len(self.tokens)

    def error(self):
        raise Exception("Invalid syntax")
    
    def __str__(self):
        return self.tokens
    
    def check_space(self):
        if (self.index >= self.num_tokens):
            return
        token = self.tokens[self.index]
        while re.match(r"\s", token):
            log.debug("space!")
            self.eat(r" ")
            if (self.index >= self.num_tokens):
                return
            token = self.tokens[self.index]
            log.debug(f"New token: {self.tokens[self.index]}")
    
    def eat(self, expect: str = r".*", num_to_jump: int = 1):
        # print("eat")
        match = re.match(expect, self.tokens[self.index:])
        if match is not None:
            self.index += num_to_jump
            self.check_space()
        else:
            print("Error: ", self.tokens[self.index:])
            self.error()

    def F(self):
        """F : -num | num | var | ( expr ) | str | bool """
        token = self.tokens[self.index]
        # print("F: ", token, self.index)
        self.check_space()

        try:
            token = re.match(r"[^\s]+", token).group()
            if token in list(Variable.vars.keys()):
                self.eat()
                return Variable.vars[token]
        except:
            None
        
        match = re.match(Tree.types["Bool"], self.tokens[self.index:])
        if match is not None:
            match = match.group()
            self.eat(Tree.types["Bool"], len(match))
            if match == "True":
                return Bool(True)
            return Bool(False)
        
        match = re.match(Tree.types["NegInt"], self.tokens[self.index:])
        if match is not None:
            match = match.group()
            self.eat(Tree.types["NegInt"], len(match))
            return NegInt(0 - int(match))
        
        match = re.match(Tree.types["Int"], self.tokens[self.index:])
        if match is not None:
            match = match.group()
            self.eat(Tree.types["Int"], len(match))
            return NegInt(int(match))
        
        elif re.match(Tree.types["LParen"], self.tokens[self.index:]):
            self.eat()
            node = self.E()
            self.eat()
            return node
        
        match = re.match(Tree.types["String"], self.tokens[self.index:])
        if match is not None:
            match = match.group()
            self.eat(Tree.types["String"], len(match))
            return String(match)
        else:
            return Nothing()

    def T(self):
        """T : T * F | T / F | F"""
        node = self.F()
        # self.check_space()

        if self.index < self.num_tokens:
            log.debug(f"Node: {node}, token: {self.tokens[self.index]}")

        while self.index < self.num_tokens and self.tokens[self.index] in "*/":
            token = self.tokens[self.index]
            if token == "*" or token == "/":
                self.eat()

            node = Operator(node, self.F(), token)
        
        # print("T: ", node)
        return node

    def E(self):
        """ 
        E : E + T | E - T | T
        """
        node = self.T()

        if self.index < self.num_tokens:
            log.debug(f"Node: {node}, token: {self.tokens[self.index]}")

        while self.index < self.num_tokens and self.tokens[self.index] in "+-":
            token = self.tokens[self.index]
            if token == "+" or token == "-":
                self.eat()

            node = Operator(node, self.T(), token)

        # print("E: ", node)
        return node
    
    def parse(self):
        return self.E()


def main():
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "ex.qk"
    # read quack

    quack = []

    assignment = r"\w+:"
    var_type = r"Int|Bool|String|Obj"
    arith_expr = r"\= \-?.+([-+*/]\-?.+)*;"


    with open(file, "r") as qk:
        lines = qk.readlines()
        for line in lines:
            if (line == "\n"):
                continue
            temp = []
            temp.append(re.match(assignment, line).group().strip(":"))
            temp.append(re.search(var_type, line).group())
            temp.append(re.search(arith_expr, line).group().strip("=;"))
            quack.append(temp)

    Obj.ASM_FILE = file.split(".")[0] + ".asm"

    try:
        open(Obj.ASM_FILE, "x")
    except FileExistsError:
        os.remove(Obj.ASM_FILE)

    # write header information
    f = open(Obj.ASM_FILE, "a")
    print(".class Calculator:Obj", file=f)
    print(".method $constructor", file=f)
    print("\tenter", file=f)

    f.close()

    log.debug(f"{quack}")

    for line in quack:
        expr = line[2].strip()
        log.debug(f"Expr: {expr}")
        eval = Tree(expr)
        eval = eval.parse()
        var = Variable(line[0], eval)
        log.debug(f"{var.name}, {var.val}")
        var.evaluate()
        # what to do with the variable...

    f = open(Obj.ASM_FILE, "a")
    print("\treturn 0", file=f)
    f.close()

if __name__ == "__main__":
    main()


