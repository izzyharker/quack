import re
import os

ASM_FILE = "test.asm"

# nodes types for Nano-quack
OBJ, INT, NEGINT, STRING, BOOL, NOTHING = range(6)

node_types = {OBJ: "OBJ", INT: "INT", NEGINT: "NEGINT", STRING: "STRING", BOOL: "BOOL", NOTHING: "NOTHING"}

class Obj():
    def __init__(self, value: None):
        self.val = value
        self.type = OBJ

    def get_type(self) -> int:
        return self.type

    def evaluate(self):
        # with open(ASM_FILE, "a") as f:
        #     print(f"\tconst {self.val}", file=f)
        # f.close()
        print(f"\tconst {self.val}")
    
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
        # with open(ASM_FILE, "a") as f:
        #     print(f"\tcall Int:{Operator.ops[self.op]}", file=f)
        # f.close()
        print(f"\tcall Int:{Operator.ops[self.op]}")
        
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
    types = {"NegInt": r"-\d+", "Int": r"\d+", "String": r"\"\w+\"", "Bool": r"True|False", "LParen": r"\(.*\)?", "RParen": r"\(?.*\)"}

    def __init__(self, expr: list[str]):
        self.index = 0
        self.tokens = expr
        self.num_tokens = len(self.tokens)

    def error(self):
        raise Exception("Invalid syntax")
    
    def __str__(self):
        return self.tokens
    
    def eat(self, expect: str = r".*"):
        if re.match(expect, self.tokens[self.index]):
            self.index += 1
        else:
            self.error()

    def F(self):
        """F : -num | num | var | ( expr ) | str"""
        token = self.tokens[self.index]
        print("F: ", token, self.index)
        if token in list(Variable.vars.keys()):
            self.eat()
            return Variable.vars[token]
        elif re.match(Tree.types["Bool"], token):
            self.eat(Tree.types["Bool"])
            if token == "true":
                return Bool(True)
            return Bool(False)
        elif re.match(Tree.types["NegInt"], token):
            self.eat(Tree.types["NegInt"])
            return NegInt(int(token))
        elif re.match(Tree.types["Int"], token):
            self.eat(Tree.types["Int"])
            return Int(int(token))
        # TODO: parentheses
        # elif re.match(Tree.types["LParen"], token):
        #     # self.tokens[self.index] = re.match(r"(.*)", token).group()
        #     self.eat()
        #     node = self.E()
        #     self.eat()
        #     return node
        elif re.match(Tree.types["String"], token):
            self.eat(Tree.types["String"])
            print(token)
            return String(token)
        else:
            return Nothing()

    def T(self):
        """T : T * F | T / F | F"""
        node = self.F()

        while self.index < self.num_tokens and self.tokens[self.index] in "*/":
            token = self.tokens[self.index]
            if token == "*" or token == "/":
                self.eat()

            node = Operator(node, self.F(), token)
        
        print("T: ", node)
        return node

    def E(self):
        """ 
        E : E + T | E - T | T
        """
        node = self.T()

        while self.index < self.num_tokens and self.tokens[self.index] in "+-":
            token = self.tokens[self.index]
            if token == "+" or token == "-":
                self.eat()

            node = Operator(node, self.T(), token)

        print("E: ", node)
        return node
    
    def parse(self):
        return self.E()
            



def main():
    # try:
    #     open(ASM_FILE, "x")
    # except FileExistsError:
    #     os.remove(ASM_FILE)

    # # write header information
    # f = open(ASM_FILE, "a")
    # print(".class Calculator:Obj", file=f)
    # print(".method $constructor", file=f)
    # print("\tenter", file=f)

    # f.close()

    quack = []

    assignment = r"\w+:"
    var_type = r"Int|Bool|String|Obj"
    arith_expr = r"\= \-?.+([-+*/]\-?.+)*;"

    # read quack
    with open("ex.qk", "r") as qk:
        lines = qk.readlines()
        for line in lines:
            if (line == "\n"):
                continue
            temp = []
            temp.append(re.match(assignment, line).group().strip(":"))
            temp.append(re.search(var_type, line).group())
            temp.append(re.search(arith_expr, line).group().strip("=;"))
            quack.append(temp)

    # build tree
    print(quack)

    for line in quack:
        expr = line[2].split()
        print(expr)
        eval = Tree(expr)
        eval = eval.parse()
        print(eval)
        var = Variable(line[0], eval)
        print(var.name)
        print(var.val)
        # what to do with the variable...

    # f = open(ASM_FILE, "a")
    # print("\treturn 0", file=f)
    # f.close()

if __name__ == "__main__":
    main()


