import re
import os
import sys
import logging as log

log.basicConfig(level=log.INFO)

# nodes types for Nano-quack
OBJ, INT, NEGINT, STRING, BOOL, NOTHING = range(6)

node_types = {OBJ: "OBJ", INT: "INT", NEGINT: "NEGINT", STRING: "STRING", BOOL: "BOOL", NOTHING: "NOTHING"}

var_types = {"Obj": OBJ, "Int": INT, "String": STRING, "Bool": BOOL}

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

    def evaluate(self):
        with open(Obj.ASM_FILE, "a") as f:
            if self.val < 0:
                print(f"\tconst 0", file=f)
                print(f"\tconst {abs(self.val)}", file=f)
                print(f"\tcall Int:minus", file=f)
            else:
                print(f"\tconst {self.val}", file=f)
        f.close()
            

# class NegInt(Obj):
#     def __init__(self, value: int):
#         super().__init__(value)
#         self.val = abs(value)
#         self.type = INT

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

    def evaluate(self):
        with open(Obj.ASM_FILE, "a") as f:
            if self.val:
                print(f"\tconst 1", file=f)
            else:
                print(f"\tconst 0", file=f)
        f.close()

class Nothing(Obj):
    def __init__(self):
        super().__init__(None)
        self.val = None
        self.type = NOTHING

class Variable(Obj):
    # vars: 
    # name: (type, number in sequence)
    expr: list[Obj] = []
    var_names: list[str] = []
    var_index = 0

    def __init__(self, name: str, given_type: str, value: Obj):
        self.name = name
        self.val = value
        self.type = var_types[given_type]

        Variable.expr.append(self)
        if self.name not in Variable.var_names:
            Variable.var_names.append(self.name)
        Variable.var_index += 1

    def get_type(self) -> int:
        return self.type
    
    def __str__(self):
        return f"{self.name}: {node_types[self.type]}"
    
    def store(self) -> None:
        self.val.evaluate()
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tstore {self.name}", file=f)
        f.close()

    def evaluate(self) -> None:
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tload {self.name}", file=f)
        f.close()

class Operator(Obj):
    # operator tree
    ops = {"+": "plus", "-": "minus", "*": "multiply", "/": "divide"}

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
    types = {"Int": r"-?\d+", "String": r"\".*\"", "Bool": r"True|False", "LParen": r"\(.*\)?", "RParen": r"\(?.*\)"}

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
        
        self.check_space()

        try:
            # look for a variable
            token = re.match(r"[^\s\)]+", self.tokens[self.index:]).group()
            # log.info(f"found {token} from {self.tokens[self.index:]}")
            if token in Variable.var_names:
                log.info(f"found a var! {token}")
                self.eat(r".*", len(token))
                for i in range(len(Variable.expr) - 1, -1, -1):
                    if Variable.expr[i].name == token:
                        return Variable.expr[i]
        except:
            None
        
        # then check bool
        match = re.match(Tree.types["Bool"], self.tokens[self.index:])
        if match is not None:
            match = match.group()
            self.eat(Tree.types["Bool"], len(match))
            if match == "True":
                return Bool(True)
            return Bool(False)
        
        # int
        match = re.match(Tree.types["Int"], self.tokens[self.index:])
        if match is not None:
            match = match.group()
            self.eat(Tree.types["Int"], len(match))
            return Int(int(match))

        # left parentheses
        elif re.match(Tree.types["LParen"], self.tokens[self.index:]):
            self.eat()
            node = self.E()
            self.eat()
            return node

        # and finally string
        match = re.match(Tree.types["String"], self.tokens[self.index:])
        if match is not None:
            match = match.group()
            self.eat(Tree.types["String"], len(match))
            return String(match)
        
        # if nothing matched, return nothing object
        else:
            return Nothing()

    def T(self):
        """T : T * F | T / F | F"""
        node = self.F()

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

    Obj.ASM_FILE = "Main.asm"

    try:
        open(Obj.ASM_FILE, "x")
    except FileExistsError:
        os.remove(Obj.ASM_FILE)

    # write header information
    f = open(Obj.ASM_FILE, "a")
    print(".class Main:Obj", file=f)
    print(".method $constructor", file=f)
    print("\t.local ", file=f, end="")

    f.close()

    log.debug(f" {quack}")

    first = True
    for line in quack:
        expr = line[2].strip()
        log.info(f" Expr: {expr}")
        eval = Tree(expr)
        eval = eval.parse()
        var = Variable(line[0], line[1], eval)
        log.info(f" {var.name}, {var.val}")

    log.info(f"{Variable.var_names}")
    
    f = open(Obj.ASM_FILE, "a")

    for name in Variable.var_names:
            if first:
                print(f"{name}", file=f, end="")
                first = False
            else:
                print(f",{name}", file=f, end="")
    
    print("\n\tenter", file=f)
    f.close()

    # print(var_list)

    for var in Variable.expr:
        var.store()

    f = open(Obj.ASM_FILE, "a")
    print("\treturn 0", file=f)
    f.close()

if __name__ == "__main__":
    main()


