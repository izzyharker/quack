import sys
import re
import os
import logging as log
import quack_builtins as qk
import AST as ast

log.basicConfig(level=log.DEBUG)

class ParseTree():
    NORMAL, CALL, EOF, ERROR = range(4)
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
        if self.pc < self.len:
            match = re.match(expect, self.program[self.pc:])
            if match is not None:
                self.pc += num_to_jump
                self.check_space()
            else:
                print("Error at:", self.program[self.pc:])
                self.state = ParseTree.ERROR
                self.error(f"Expected token {expect} not found in {self.program[self.pc:]}")
        else:
            self.state = ParseTree.EOF
            return

    def literal(self):
        """
        integer, var_name, string, bool
        """
        integer = r"(-?[1-9]\d*)|0"
        string = r"\".*\""
        var_name = r"if"
        for var in qk.Variable.var_names:
            var_name += rf"|{var}"
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
        
        # check not a keyword
        match = re.match(qk.keywords + r"[^\w^\_]", self.program[self.pc:])
        if match is None:
            # look for variable name
            # log.debug(f"variable ={self.program[self.pc:]}")
            match = re.match(var_name, self.program[self.pc:])
            if match is not None:
                match = match.group()
                log.debug(f"existing variable -{match}-")
                for var in qk.Variable.expr:
                    # log.debug(f"checking -{match}- against -{var.name}-")
                    if var.name == match:
                        log.debug(f"found var {var}")
                        self.eat(num_to_jump=len(match))
                        return var
            match = re.match(r"[\w\_]+", self.program[self.pc:])
            if match is not None:
                match = match.group()
                log.debug(f"new variable -{match}-")
                self.eat(num_to_jump=len(match))
                return qk.Variable(match, qk.NOTHING, None)
            # self.error("NameError: Reference to Undefined Variable")

        log.debug(f"Unrecognized literal:{self.program[self.pc:self.pc+12]} - returning Nothing()")
        return qk.Nothing()

    def ident(self):
        # variable name - covered under literal
        # this is for lhs/assignment so doesn't depend on previous instantiation
        
        # check that its not a keyword
        match = re.match(qk.keywords + r"[^\w^\_]", self.program[self.pc:])
        if match is None:
            match = re.match(r"[\w\_]+", self.program[self.pc:])
            if match is not None:
                match = match.group()
                self.eat(num_to_jump=len(match))
                log.debug(f"match={match}")
                if re.match(r"\(", self.program[self.pc]):
                    self.state = ParseTree.CALL
                    self.eat(r"\(")
                    self.eat(r"\)")
                    return ast.Call(None, match)
                self.state = ParseTree.NORMAL
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

        # if self.pc < self.len:
        #     log.debug(f"Node: {node}, token: {self.program[self.pc]}")

        while self.pc < self.len and self.program[self.pc] in "*/":
            token = self.program[self.pc]
            if token == "*" or token == "/":
                self.eat()

            node = ast.Expression(node, self.literal(), token)
        
        # print("T: ", node)
        return node

    def R_Expr(self):
        """ 
        E : E + T | E - T | T

        TODO: add conditionals
        """
        match = re.match(r"not", self.program[self.pc:])
        if match is not None:
            node = ast.Not(self.R_Expr())
            return node
        
        node = self.rexpr_times()
        # if self.pc < self.len:
        #     log.debug(f"Node: {node}, token: {self.program[self.pc]}")

        while self.pc < self.len and self.program[self.pc] in "+-":
            token = self.program[self.pc]
            if token == "+" or token == "-":
                self.eat()

            log.debug(f"found token: {token}")
            node = ast.Expression(node, self.rexpr_times(), token)

        match = re.match(r"<|>|==|<=|>=", self.program[self.pc]) 
        if match is not None:
            match = match.group()
            self.eat(match, len(match))
            node = ast.IntComp(node, self.R_Expr(), match)

        match = re.match(r"and|or", self.program[self.pc:])
        if match is not None:
            match = match.group()
            self.eat(match, len(match))
            node = ast.BoolComp(node, self.R_Expr(), match)

        # print("E: ", node)
        return node

    # leave user-written method calls to later
    def L_Expr(self):
        """
        ident | ident.ident
        """
        expr = self.R_Expr()
        log.debug(f"expr: {expr}")
        rhs = None
        if self.program[self.pc] == ".":
            self.eat(r"\.")
            log.debug(f"at {self.program[self.pc:self.pc + 12]}")
            rhs = self.ident()
            if self.state == ParseTree.CALL:
                rhs.assign_var(expr)
                log.debug(f"Calling {rhs.method} on {expr}")
                self.state = ParseTree.NORMAL
                return rhs
            elif self.state == ParseTree.NORMAL:
                return qk.Variable.var_names[expr.val]

        return expr
    
    def ElifBlock(self) -> ast.ElifNode | None:
        block = []
        if re.match(r"elif", self.program[self.pc:]) is not None:
            self.eat(r"elif", num_to_jump=4)
            elifcond = self.R_Expr()
            log.debug(f"elif condition located: {elifcond}")
            if re.match(r";", self.program[self.pc]) is not None:
                # else
                self.eat(r";")
            else:
                self.eat(r"\{")
                self.Statement_Block(end_char = r"\}", block=block)
            return ast.ElifNode(elifcond, ast.Block(block))
        else:
            return None

    def ElseBlock(self) -> ast.Conditional | None:
        block = []
        if re.match(r"else", self.program[self.pc:]) is not None:
            self.eat(r"else", num_to_jump=4)
            if re.match(r";", self.program[self.pc]) is not None:
                # else
                self.eat(r";")
            else:
                self.eat(r"\{")
                self.Statement_Block(end_char = r"\}", block=block)
            elsenode = ast.ElseNode(ast.Block(block))
            return elsenode
        else:
            return None
    
    def IfBlock(self) -> ast.IfNode:
        if re.match(r"if", self.program[self.pc:]) is not None:
            self.eat(r"if", 2)
            ifcond = self.R_Expr()
            log.debug(f"If condition located: {ifcond}")
            block = []
            if re.match(r";", self.program[self.pc]) is not None:
                # else
                self.eat(r";")
            else:
                self.eat(r"\{")
                self.Statement_Block(end_char = r"\}", block=block)
            ifnode = ast.IfNode(ifcond, ast.Block(block))
            return ifnode

    def Conditional(self) -> ast.Conditional:
        ifnode = self.IfBlock()
        elifnodes = []
        while re.match(r"elif", self.program[self.pc:]) is not None:
            elifnodes.append(self.ElifBlock())
        elsenode = self.ElseBlock()
        return ast.Conditional(ifnode, elifnodes, elsenode)

    def While(self) -> ast.While:
        whilecond = self.R_Expr()
        log.debug(f"While condition located: {whilecond}")
        block = []
        if re.match(r";", self.program[self.pc]) is not None:
            # else
            self.eat(r";")
        else:
            self.eat(r"\{")
            self.Statement_Block(end_char = r"\}", block=block)
        whilenode = ast.While(whilecond, ast.Block(block))
        return whilenode

    def Statement(self, nested: list = None):
        """
        l_expr [: class]? = r_expr ;
        r_expr "." method()
        if (cond) {
            statement
        }
        """
        if re.match(r"if[\s\(]", self.program[self.pc:]):
            node = self.Conditional()
            if nested is None:
                ParseTree.statements.append(node)
            else:
                nested.append(node)
            return
        elif re.match(r"while[\s\(]", self.program[self.pc:]):
            self.eat("", num_to_jump=5)
            node = self.While()
            if nested is None:
                ParseTree.statements.append(node)
            else:
                nested.append(node)
            return
        else:    
            log.debug(f"L_Expr or method call: {self.program[self.pc:self.pc + 12]}")
            l_expr = self.L_Expr()
            declared_type = None
            if self.state is not ParseTree.EOF:
                if self.program[self.pc] == ":":
                    self.eat(r":")
                    declared_type = self.class_ident()
                
                if self.program[self.pc] == "=":
                    self.eat(r"=")
                    r_expr = self.R_Expr()
                    self.eat(";")
                    l_expr.assign(r_expr, r_expr.type)
                    stmt = ast.Assign(l_expr, r_expr, declared_type)

                    if nested is None:
                        ParseTree.statements.append(stmt)
                    else:
                        nested.append(stmt)
                    log.debug(f"{stmt}")
                    return
                
            if nested is None:
                ParseTree.statements.append(l_expr)
            else:
                nested.append(l_expr)
            self.eat(";")
        return


    def Statement_Block(self, end_char = None, block = None):
        if end_char is None:
            while self.pc < self.len:
                self.Statement()
        else:
            while self.pc < self.len and re.match(end_char, self.program[self.pc:]) is None:
                self.Statement(block)
            self.eat(end_char, len(end_char))
        return

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

    out_file = file.split(".")[0]

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

    qk.Obj.ASM_FILE = f"{out_file}.asm"

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

    f = open(qk.Obj.ASM_FILE, "a")
    print("\treturn 0", file=f)
    f.close()

    log.debug("done")

if __name__ == "__main__":
    main()