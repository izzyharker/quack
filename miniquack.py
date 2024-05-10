import sys
import re
import os
import logging as log
import quack_builtins as qk

log.basicConfig(level=log.DEBUG)

class ParseTree():
    NORMAL, EOF, ERROR = range(3)
    var_names = []
    var_types: dict[str: int] = {}

    # list of things to evaluate, in order of appearance
    statements = []

    def __init__(self, program: str):
        """
        Initiates the ParseTree with a program
        """
        self.program = program
        self.len = len(program)
        self.pc = 0

        # placeholder for now - may not need this in the end
        self.state = ParseTree.NORMAL

    def __str__(self):
        return f"position {self.pc}, '{self.program[self.pc]}'"
    
    def error(self, msg = ""):
        raise Exception(msg)

    def check_space(self):
        if (self.pc >= self.len):
            self.state = ParseTree.EOF
            return
        token = self.program[self.pc]
        # log.info(f"space token:{token}.")
        while re.match(r"[\s\n]", token) is not None:
            # log.debug("space!")
            self.eat(r"\s", 1)
            if (self.pc >= self.len):
                self.state = ParseTree.EOF
                return
            token = self.program[self.pc]
    
    def eat(self, expect: str = r".", num_to_jump: int = 1):
        # print("eat")
        match = re.match(expect, self.program[self.pc:])
        if match is not None:
            self.pc += num_to_jump
            self.check_space()
        else:
            print("Error at:", self.program[self.pc:])
            self.state = ParseTree.ERROR
            self.error(f"Expected token {expect} not found in {self.program[self.pc:]}")

    def literal(self):
        """
        integer, var_name, string, bool
        """
        integer = r"-?[1-9]\d*"
        string = r"\".*\""
        var_name = r""
        for var in qk.Variable.var_names:
            var_name += rf"{var}|"
        boolean = r"true|false"

        self.check_space()

        # log.debug(f"Current literal token: {self.program[self.pc]}")
        # need to do lparen first
        if self.program[self.pc] == "(":
            self.eat(r"\(")
            node = self.R_Expr()
            self.eat(r"\)")
            log.debug(f"After parens: {self.program[self.pc]}")
            return node

        match = re.match(boolean, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            self.eat(boolean, len(match))
            return qk.Bool(match)

        match = re.match(var_name, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            self.eat(num_to_jump=len(match))
            for v in qk.Variable.expr:
                if v.name == match:
                    return v
            # self.error("NameError: Reference to Undefined Variable")
        
        match = re.match(string, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            self.eat(num_to_jump=len(match))
            return qk.String(match)
        
        match = re.match(integer, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            self.eat(num_to_jump=len(match))
            return qk.Int(int(match))

        log.debug(f"Unrecognized literal {self.program[self.pc:self.pc+12]} - returning Nothing()")
        return qk.Nothing()

    def ident(self):
        # variable name - covered under literal
        # this is for lhs/assignment so doesn't depend on previous instantiation
        
        # check that its not a keyword
        match = re.match(qk.keywords + r"[^\w^\_]", self.program)
        if match is None:
            match = re.match(r"[\w\_]+", self.program[self.pc:])
            if match is not None:
                match = match.group()
                self.eat(num_to_jump=len(match))
                return match
            self.state = ParseTree.ERROR
            return None
        else:
            self.error("Variable name cannot be a keyword!")

    def class_ident(self):
        # eventually have this be a list of declared classes
        classes = r"Obj|Int|String|Boolean|Nothing"
        self.check_space()
        match = re.match(classes, self.program[self.pc:])
        log.debug(f"Current index:{self.program[self.pc:self.pc + 12]}")
        if match is not None:
            match = match.group()
            log.debug(f"class: {match}")
            self.eat(num_to_jump=len(match))
            return qk.var_types[match]
        self.state = ParseTree.ERROR
        self.error(f"TypeError: Undefined class:{self.program[self.pc:]}")

    def Method_Call(self):
        # skip this for now - this will be obj.function()
        pass

    def rexpr_times(self):
        """T : T * F | T / F | F"""
        node = self.literal()

        if self.pc < self.len:
            log.debug(f"Node: {node}, token: {self.program[self.pc]}")

        while self.pc < self.len and self.program[self.pc] in "*/":
            token = self.program[self.pc]
            if token == "*" or token == "/":
                self.eat()

            node = qk.Operator(node, self.literal(), token)
        
        # print("T: ", node)
        return node

    def R_Expr(self):
        """ 
        E : E + T | E - T | T
        """
        node = self.rexpr_times()

        if self.pc < self.len:
            log.debug(f"Node: {node}, token: {self.program[self.pc]}")

        while self.pc < self.len and self.program[self.pc] in "+-":
            token = self.program[self.pc]
            if token == "+" or token == "-":
                self.eat()

            log.debug(f"found token: {token}")
            node = qk.Operator(node, self.rexpr_times(), token)

        # print("E: ", node)
        return node

    # leave user-written method calls to later
    def L_Expr(self):
        """
        ident | ident.ident
        """
        # need to figure out how to make this work for variables
        # nano-quack is now broken
        expr = self.literal()
        rhs = None
        if self.program[self.pc] == ".":
            self.eat(r"\.")
            rhs = self.ident()

        if re.match(r"\(\)", self.program[self.pc:]):
            self.eat()
            self.eat()
            return qk.Call(expr, rhs)

    def Statement(self):
        """
        l_expr [: class]? = r_expr ;
        r_expr "." method()
        """

        # TODO: change literal for variables to check on evaluate intead of on parse
        l_expr = self.L_Expr()
        declared_type = qk.NOTHING
        if self.state is not ParseTree.EOF:
            if self.program[self.pc] == ":":
                self.eat(r":")
                declared_type = self.class_ident()
            
            if self.program[self.pc] == "=":
                self.eat(r"=")
                r_expr = self.R_Expr()
                self.eat(";")
                stmt = qk.Variable(l_expr, declared_type, r_expr)
                ParseTree.statements.append(stmt)
                self.eat(";")
                return
            
        ParseTree.statements.append(l_expr)
        self.eat(";")


    def Statement_Block(self):
        while self.pc < self.len:
            self.Statement()

    def Conditional(self):
        pass

    # for later
    def Method(self):
        pass

    # for later
    def Args(self):
        pass

    # for later
    def Class_Signature(self):
        pass

    # for later
    def Class(self):
        pass

    def evaluate(self):
        return self.Statement_Block()

def main():
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "method.qk"
    # read quack

    quack = []

    assignment = r"\w+:"
    var_type = r"Int|Bool|String|Obj"
    arith_expr = r"\= \-?.+([-+*/]\-?.+)*;"

    program = ""

    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if (line == "\n"):
                continue
            else:
                program += line

    qk.Obj.ASM_FILE = "test.asm"

    try:
        open(qk.Obj.ASM_FILE, "x")
    except FileExistsError:
        os.remove(qk.Obj.ASM_FILE)

    # write header information
    f = open(qk.Obj.ASM_FILE, "a")
    print(".class Main:Obj", file=f)
    print(".method $constructor", file=f)
    print("\t.local ", file=f, end="")

    f.close()

    tree = ParseTree(program)
    tree.evaluate()

    f = open(qk.Obj.ASM_FILE, "a")
    first = True
    for name in qk.Variable.var_names:
            if first:
                print(f"{name}", file=f, end="")
                first = False
            else:
                print(f",{name}", file=f, end="")
    
    print("\n\tenter", file=f)
    f.close()

    for expr in ParseTree.statements:
        expr.evaluate()
        # expr.store()

    f = open(qk.Obj.ASM_FILE, "a")
    print("\treturn 0", file=f)
    f.close()

    log.debug("done")

if __name__ == "__main__":
    main()