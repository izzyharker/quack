import sys
import re
import os
import logging as log
import quack_builtins as qk
import AST as ast

log.basicConfig(level=log.DEBUG)

class ParseTree():
    NORMAL, EOF, CLASS = range(3)
    var_names = []
    classes = []
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

    def check_comment(self) -> None:
        match = re.match(r"//.*\n", self.program[self.pc:])
        if match is not None:
            match = match.group()
            self.eat(r"//.*\n", len(match))
            return
        
        match = re.match(r"/\*.*\*/", self.program[self.pc:])
        if match is not None:
            match = match.group()
            self.eat(r"/\*.*\*/", len(match))
            return
    
    def eat(self, expect: str = r".", num_to_jump: int = 1) -> None:
        # print("eat")
        if self.pc < self.len:
            match = re.match(expect, self.program[self.pc:])
            if match is not None:
                self.pc += num_to_jump
                self.check_space()
                self.check_comment()
            else:
                print("Error at:", self.program[self.pc:])
                self.error(f"Expected token {expect} not found in {self.program[self.pc:]}")
        else:
            self.state = ParseTree.EOF
        return

    def literal(self):
        """
        integer, var_name, string, bool
        """
        integer = r"(-?[1-9]\d*)|0"
        # TODO: fix string thing
        string = r"\".*\""
        longstring = f"\"\"\".*\"\"\""
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
        
        match = re.match(longstring, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            log.debug(f"Long string: {match}")
            self.eat(num_to_jump=len(match))
            return qk.String(match)
        
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
                return match
            return None
        else:
            self.error("Variable name cannot be a keyword!")

    def class_ident(self):
        # eventually have this be a list of declared classes
        classes = r"Obj|Int|String|Boolean|Nothing"
        for c in ParseTree.classes:
            classes += rf"|{c.name}"
        self.check_space()
        match = re.match(classes, self.program[self.pc:])
        log.debug(f"Current index:{self.program[self.pc:self.pc + 12]}")
        if match is not None:
            match = match.group()
            log.debug(f"class: {match}")
            self.eat(num_to_jump=len(match))
            return qk.var_types[match]
        self.error(f"TypeError: Undefined class:{self.program[self.pc:]}")

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
    
    def R_intcomp(self):
        node = self.rexpr_times()

        match = re.match(r"<=|>=|==|<|>", self.program[self.pc:]) 
        if match is not None:
            match = match.group()

            self.eat(match, len(match))
            node = ast.IntComp(node, self.R_Expr(), match)
        
            log.debug(f"Intcomp: {node}")
        else:
            log.debug(f"{node}")
        return node
    
    def Class_Instance(self) -> ast.UserClassInstance :
        classes = r"Obj|Int|String|Boolean|Nothing"
        for c in ParseTree.classes:
            classes += rf"|{c}"
        self.check_space()
        match = re.match(classes, self.program[self.pc:])
        log.debug(f"Current index:{self.program[self.pc:self.pc + 12]}")
        if match is not None:
            match = match.group()
            log.debug(f"New class instance: {match}")
            self.eat(num_to_jump=len(match))
            self.eat(r"\(")
            args = [self.literal()]
            while re.match(r"\)", self.program[self.pc:]) is None:
                self.eat(r",")
                args.append(self.literal())
            self.eat(r"\)")
            return ast.UserClassInstance(match, args)
        return None


    def R_Expr(self):
        """ 
        E : E + T | E - T | T

        TODO: add conditionals
        """
        match = re.match(r"not", self.program[self.pc:])
        if match is not None:
            node = ast.Not(self.R_Expr())
            return node
        
        node = self.R_intcomp()
        # if self.pc < self.len:
        #     log.debug(f"Node: {node}, token: {self.program[self.pc]}")

        while self.pc < self.len and self.program[self.pc] in "+-":
            token = self.program[self.pc]
            if token == "+" or token == "-":
                self.eat()

            log.debug(f"found token: {token}")
            node = ast.Expression(node, self.rexpr_times(), token)

        return node

    def R_andor(self):
        node = self.Class_Instance()

        if node is None:
            node = self.R_Expr()

            match = re.match(r"and|or", self.program[self.pc:])
            if match is not None:
                match = match.group()
                self.eat(match, len(match))
                log.debug(f"Boolcomp: {node}")
                node = ast.BoolComp(node, self.R_Expr(), match)

            # print("E: ", node)
        return node

    # leave user-written method calls to later
    def L_Expr(self) -> ast.Call | ast.Field | qk.Variable :
        """
        ident | ident.ident
        """
        expr = self.R_andor()
        log.debug(f"expr: {expr}")
        rhs = None
        # if field access or method call, do something different
        if self.program[self.pc] == ".":
            self.eat(r"\.")
            log.debug(f"at {self.program[self.pc:self.pc + 12]}")
            # identify
            rhs = self.ident()
            # this triggers on "("
            if re.match(r"\(", self.program[self.pc:]):
                self.eat(r"\(")
                args = self.Args()
                self.eat(r"\)")
                rhs = ast.Call(None, rhs, args)
                rhs.assign_var(expr)
                log.debug(f"Calling {rhs.method} on {expr}")
                return rhs
            # otherwise return a field access instance with the value and the rhs
            else:
                rhs = ast.Field(None, rhs)
                rhs.set_var(expr)
                log.debug(f"Field access: {rhs}")
            return rhs

        return expr
    
    def ElifBlock(self) -> ast.ElifNode | None:
        block = []
        if re.match(r"elif", self.program[self.pc:]) is not None:
            self.eat(r"elif", num_to_jump=4)
            elifcond = self.L_Expr()
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
            if re.match(r"\(.*\)", self.program[self.pc:]):
                self.eat(r"\(", 1)
                ifcond = self.L_Expr()
                log.debug(f"If condition located: {ifcond}")
                block = []
                if re.match(r"\)", self.program[self.pc:]):
                    self.eat(r"\)", 1)
                if re.match(r";", self.program[self.pc]) is not None:
                    # else
                    self.eat(r";")
                else:
                    self.eat(r"\{")
                    self.Statement_Block(end_char = r"\}", block=block)
                ifnode = ast.IfNode(ifcond, ast.Block(block))
                return ifnode
            else:
                self.error("Missing parentheses around IF condition")

    def Conditional(self) -> ast.Conditional:
        ifnode = self.IfBlock()
        elifnodes = []
        while re.match(r"elif", self.program[self.pc:]) is not None:
            elifnodes.append(self.ElifBlock())
        elsenode = self.ElseBlock()
        return ast.Conditional(ifnode, elifnodes, elsenode)

    def While(self) -> ast.While:
        whilecond = self.L_Expr()
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
        if nested is None:
            block = ParseTree.statements
        else:
            block = nested
        self.check_comment()
        # check if
        if re.match(r"if[\s\(]", self.program[self.pc:]):
            node = self.Conditional()
            block.append(node)
            return
        
        # check while
        elif re.match(r"while[\s\(]", self.program[self.pc:]):
            self.eat("", num_to_jump=5)
            node = self.While()
            block.append(node)
            return
        
        # 
        else:    
            log.debug(f"L_Expr or method call: {self.program[self.pc:self.pc + 12]}")
            l_expr = self.L_Expr()
            declared_type = None
            if self.state is not ParseTree.EOF:
                # check declaring type
                if self.program[self.pc] == ":":
                    self.eat(r":")
                    declared_type = self.class_ident()
                
                # assignment
                if self.program[self.pc] == "=":
                    self.eat(r"=")
                    r_expr = self.L_Expr()
                    self.eat(";")
                    l_expr.assign(r_expr, r_expr.type)
                    log.debug(f"l_expr: {l_expr}")
                    stmt = ast.Assign(l_expr, r_expr, declared_type)

                    block.append(stmt)
                    log.debug(f"{stmt}")
                    return
                
            # method call/etc.
            block.append(l_expr)

            # endline
            self.eat(";")
        return


    def Statement_Block(self, end_char = None, block = None):
        if end_char is None:
            while self.pc < self.len:
                self.Statement()
        else:
            while self.pc < self.len and re.match(end_char, self.program[self.pc:]) is None:
                if re.match(r"def", self.program[self.pc:]):
                    return
                self.Statement(block)
            self.eat(end_char)
        return

    # for later
    def Args(self):
        args = ast.Params()
        if re.match(r"\(", self.program[self.pc]) is not None:
            self.eat(r"\(", 1)
        while re.match(r"\)", self.program[self.pc]) is None:
            name = self.ident()
            self.eat(r":")
            tpe = self.class_ident()
            args.add_param((name, tpe))
            try:
                self.eat(r",")
            except:
                continue
        return args

    def Method(self):
        if re.match(r"def", self.program[self.pc:]) is not None:
            # get name
            self.eat(r"def", 3)
            name = self.ident()

            # get args
            self.eat(r"\(", 1)
            args = self.Args()
            self.eat(r"\)", 1)

            # get return type
            self.eat(r":", 1)
            ret = self.class_ident()
            self.eat(r"\{", 1)

            # parse statements
            block = []
            self.Statement_Block(end_char = r"\}", block=block)
            method = ast.Method(name, args, ret, block)
            log.debug(f"{method}")
            # return
            return method
        else:
            # this should never never happen
            self.error(f"Error: attempted method parsing at {self.program[self.pc + 12]}")

    def ClassBody(self):
        # classbody is a sequence of statements followed by a sequence of method definitions
        body = ast.ClassBody(self.Statement_Block(end_char=r"\}"))
        log.debug(f"finished statements, looking for method call at {self.program[self.pc:self.pc + 12]}")
        while self.pc < self.len and re.match(r"def", self.program[self.pc:]) is not None:
            log.debug("Found a new method!")
            body.add_method(self.Method())
        self.eat(r"\}")
        return body

    # for later
    def Class(self):
        self.state = ParseTree.CLASS
        match = re.match(r"class", self.program[self.pc:])
        # this is a bit redundant but whatever
        if match is not None:
            self.eat(r"class", 5)
            classname = self.ident()
            # get the function arguments
            self.eat(r"\(", 1)
            args = self.Args()
            self.eat(r"\)", 1)
        match = re.match(r"extends", self.program[self.pc:])
        if match is not None:
            self.eat(r"extends", len("extends"))
            parent = self.class_ident()
            log.debug(f"new class {classname} extending {parent}")
        else:
            parent = qk.OBJ
            log.debug(f"no parent given, new class {classname} inheriting Obj")
        self.eat(r"\{")

        self.state = ParseTree.CLASS
        new_class = ast.Class(classname, args, self.ClassBody(), parent)
        log.debug(f"{new_class}")
        ParseTree.classes.append(new_class.name)
        return

    def evaluate(self):
        # evaluate 0 or more class statements
        while self.pc < self.len and re.match(r"class", self.program[self.pc:]) is not None:
            self.Class()
        
        log.debug("Finished parsing class definitions - looking for statements...")
        log.debug(f"Current position: {self.program[self.pc:self.pc + 12]}")
        # followed by a statement block
        self.Statement_Block()

def main():
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "ex.qk"
    # read quack

    path = ""
    out_file = file.split(".")[0]
    if file.startswith("qk_test/"):
        path = "qk_test/"
        out_file = file.split("/")[1].split(".")[0]

    out_file = out_file[0].upper() + out_file[1:]
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
    print(f".class {out_file}:Obj", file=f)
    print(".method $constructor", file=f, end="")

    f.close()

    tree = ParseTree(program)
    tree.evaluate()

    f = open(qk.Obj.ASM_FILE, "a")
    first = True
    if len(qk.Variable.var_names) > 0:
        print("\n\t.local ", file=f, end="")
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