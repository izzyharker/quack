import sys
import re
import os
from AST import *
# import logging as log
# import warnings

# log.basicConfig(level=log.DEBUG)

class ParseTree():
    NORMAL, EOF, CLASS, RETURN = range(4)
    statements = []
    classes = []

    def __init__(self, program: str):
        """
        Initiates the ParseTree with a given program string
        """
        self.program = program
        self.len = len(program)
        # program counter
        self.pc = 0

        self.state = ParseTree.NORMAL

    def __str__(self):
        return f"position {self.pc}, '{self.program[self.pc]}'"
    
    def error(self, msg = ""):
        raise Exception(msg)
    
    def check_space(self):
        # If we run off the end of the program, return
        if (self.pc >= self.len):
            self.state = ParseTree.EOF
            return
        
        # Otherwise, keeping checking if there's a space until none is found
        token = self.program[self.pc]
        while re.match(r"[\s\n]", token) is not None:
            # log.debug("space!")
            self.eat(r"\s", 1)
            if (self.pc >= self.len):
                self.state = ParseTree.EOF
                return
            token = self.program[self.pc]

    def check_comment(self) -> None:
        # eat short-form comment
        match = re.match(r"//.*\n", self.program[self.pc:])
        if match is not None:
            match = match.group()
            self.eat(r"//.*\n", len(match))
            return
        
        # eat long form comment
        match = re.match(r"/\*.*\*/", self.program[self.pc:])
        if match is not None:
            match = match.group()
            self.eat(r"/\*.*\*/", len(match))
            return
        
    def eat(self, expect: str = r".", num_to_jump: int = 1) -> None:
        # eats a token
        # check if still in program
        if self.pc < self.len:
            match = re.match(expect, self.program[self.pc:])
            if match is not None:
                self.pc += num_to_jump
                self.check_space()
                self.check_comment()
            else:
                # log.info(f"Error at: {self.program[self.pc:]}")
                self.error(f"Expected token {expect} not found in {self.program[self.pc:]}")
        else:
            self.state = ParseTree.EOF
        return
    
    def literal(self):
        integer = r"(-?[1-9]\d*)|0"

        # short strings accept character that they technically shouldn't - this was not high priority to fix. 
        string = r"\"[^\"]*\""
        longstring = f"\"\"\".*\"\"\""
        boolean = r"true|false"

        self.check_space()

        # check for left parentheses
        if self.program[self.pc] == "(":
            self.eat(r"\(")
            node = self.R_Expr()
            self.eat(r"\)")
            log.debug(f"Parsed expression ({node})")
            return node

        # boolean
        match = re.match(boolean, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            self.eat(boolean, len(match))
            return Bool(match)
        
        # check for variable name first. If found, return early
        node = self.ident()

        if node is not None:
            return node
        
        # long form string
        match = re.match(longstring, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            log.debug(f"Long string: {match}")
            self.eat(num_to_jump=len(match))
            return String(match)
        
        # short form string
        match = re.match(string, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            log.debug(f"Short string literal: {match}")
            self.eat(num_to_jump=len(match))
            return String(match)
        
        # integer
        match = re.match(integer, self.program[self.pc:]) 
        if match is not None:
            match = match.group()
            self.eat(num_to_jump=len(match))
            return Int(int(match))
        
        # The above are all disjoint, so order of checking doesn't matter. If none match, return unrecognized literal. 
        # this return is likely the sign of a different error, either in the parser or in the program. 

        log.debug(f"Unrecognized literal:{self.program[self.pc:self.pc+12]} - returning Nothing()")
        return Nothing()
    
    def ident(self):
        keywords = r"class|if|while|and|typecase|def|elif|return|or|not|extends|else|String|Int|Obj|Boolean|true|false|Nothing|none"
        self.check_space()

        # check that the ident is not a keyword - keyword followed by not an underscore or alphanumeric character.
        match = re.match(keywords + r"[^\w^\_]", self.program[self.pc:])
        if match is None:
            # now check variable name - start with letter, then any letter, digit, or underscore
            match = re.match(r"[a-zA-Z][\w\_]*", self.program[self.pc:])
            if match is not None:
                match = match.group()
                self.eat(num_to_jump=len(match))
                log.debug(f"Ident: {match}")

                # An ident can be a variable, class, type, etc., so just return the string and decide what it is based on context. 
                return match
            return None
        else:
            self.error(f"Ident {match.group()} cannot be a keyword!")

    # Killing class_ident() because moving type checks to AST instead of ParseTree.

    def Calling_Args(self):
        args = []

        # check for starting paren
        if re.match(r"\(", self.program[self.pc]) is not None:
            self.eat(r"\(", 1)
        # check if method takes no args first
        if self.program[self.pc] == ")":
            self.eat(r"\)")
            return args
        
        while True:
            args.append(self.literal())
            if re.match(r",", self.program[self.pc:]) is None:
                if re.match(r"\)", self.program[self.pc:]) is None:
                    self.error(f"Expected ',' or ')' to end arguments, got {self.program[self.pc:self.pc + 12]}")
                break
            self.eat(r",")

        self.eat(r"\)")
        return args
    
    def Class_Instance(self) -> UserClassInstance :
        match = self.literal()

        if isinstance(match, str) and self.program[self.pc] == "(":
            log.debug(f"Class instance: {match}")
            self.eat(num_to_jump=len(match))
            args = self.Calling_Args()
            inst = UserClassInstance(match, args)
            return inst
        
        return match

    def R_Expr_Field(self) -> str | Obj | Field | Call:
        """
        x.y
        This takes precedence over times because it is unary.
        """
        # identify lhs
        node = self.Class_Instance()

        if isinstance(node, UserClassInstance):
            return node

        rhs = None
        # if we see a '.', parse it
        while self.program[self.pc] == ".":
            self.eat()
            # get rhs (this must be an ident)
            rhs = self.ident()
            # if (), we have a method call - parse arguments and break
            args = []
            if re.match(r"\(", self.program[self.pc:]):
                self.eat(r"\(")
                args = self.Calling_Args()
                log.debug(f"At {self.program[self.pc:self.pc+12]}")
                node = Call(node, rhs, args)
                break
            # otherwise, set field node
            node = Field(node, rhs)
        
        return node

    def R_Expr_Times(self):
        """
        *, / operators
        This is the highest precedence operator, so lowest in parse tree
        """
        node = self.R_Expr_Field()

        # If we have a times, parse it and return the Expression
        while self.pc < self.len and self.program[self.pc] in ['*', '/']:
            token = self.program[self.pc]
            self.eat()
            node = Expression(node, self.R_Expr_Field(), token)

        # Otherwise, return only the literal
        return node
    
    def R_Expr_Plus(self):
        """
        +, - operators
        """
        node = self.R_Expr_Times()

        # If we have a times, parse it and return the Expression
        while self.pc < self.len and self.program[self.pc] in ['+', '-']:
            token = self.program[self.pc]
            self.eat()
            node = Expression(node, self.R_Expr_Times(), token)

        # Otherwise, return only the literal
        return node


    def R_Expr_IntComp(self):
        """
        Comparison operators - ==, <, etc.
        less, equals have to be defined methods for a class for these to work. greater doesn't matter. 
        """
        node = self.R_Expr_Plus()

        match = re.match(r"<=|>=|==|<|>", self.program[self.pc:]) 
        if match is not None:
            match = match.group()

            self.eat(match, len(match))
            node = IntComp(node, self.R_Expr_Plus(), match)
        
            log.debug(f"Comparison: {node}")
        else:
            log.debug(f"{node}")
        return node

    def R_Expr_AndOr(self):
        node = self.R_Expr_IntComp()

        match = re.match(r"and|or", self.program[self.pc:])
        if match is not None:
            match = match.group()
            self.eat(match, len(match))
            node = BoolComp(node, self.R_Expr_AndOr(), match)
            log.debug(r"And/Or: {node}")
        return node
    
    def R_Expr(self):
        match = re.match(r"not", self.program[self.pc:])
        if match is not None:
            self.eat(r"not")
            node = Not(self.R_Expr())
            
        else:
            node = self.R_Expr_AndOr()

        return node
    
    def L_Expr(self):
        lhs = self.R_Expr()
        log.debug(f"lhs: {lhs}")
        decl_type = None
        if self.program[self.pc] == ':':
            self.eat(r":")
            decl_type = self.ident()
        
        if self.program[self.pc] == "=":
            self.eat(r"=")
            rhs = self.R_Expr()
            lhs = Assign(lhs, rhs, decl_type)

        return lhs

    def ElifBlock(self) -> ElifNode | None:
        block = []
        if re.match(r"elif", self.program[self.pc:]) is not None:
            self.eat(r"elif", num_to_jump=4)
            self.eat(r"\(")
            elifcond = self.R_Expr()
            if self.program[self.pc] == ")":
                self.eat(r"\)")
            log.debug(f"elif condition located: {elifcond}")
            if re.match(r";", self.program[self.pc]) is not None:
                # else
                self.eat(r";")
            else:
                self.eat(r"\{")
                self.Statement_Block(end_char = r"\}", block=block)
            return ElifNode(elifcond, Block(block))
        else:
            return None

    def ElseBlock(self) -> Conditional | None:
        block = []
        if re.match(r"else", self.program[self.pc:]) is not None:
            self.eat(r"else", num_to_jump=4)
            if re.match(r";", self.program[self.pc]) is not None:
                # else
                self.eat(r";")
            else:
                self.eat(r"\{")
                self.Statement_Block(end_char = r"\}", block=block)
            elsenode = ElseNode(Block(block))
            return elsenode
        else:
            return None
    
    def IfBlock(self) -> IfNode:
        if re.match(r"if", self.program[self.pc:]) is not None:
            self.eat(r"if", 2)
            if re.match(r"\(.*\)", self.program[self.pc:]):
                self.eat(r"\(", 1)
                log.debug(f"Condition at {self.program[self.pc:]}")
                ifcond = self.R_Expr()
                log.debug(f"If condition located: {ifcond}, {ifcond.type}")
                block = []
                if re.match(r"\)", self.program[self.pc:]):
                    self.eat(r"\)", 1)
                if re.match(r";", self.program[self.pc]) is not None:
                    # else
                    self.eat(r";")
                else:
                    self.eat(r"\{")
                    self.Statement_Block(end_char = r"\}", block=block)
                ifnode = IfNode(ifcond, Block(block))
                return ifnode
            else:
                self.error("Missing parentheses around IF condition")

    def Conditional(self) -> Conditional:
        log.debug(f"Parsing conditional at {self.program[self.pc:self.pc + 12]}")
        ifnode = self.IfBlock()
        elifnodes = []
        while re.match(r"elif", self.program[self.pc:]) is not None:
            elifnodes.append(self.ElifBlock())
        elsenode = self.ElseBlock()
        return Conditional(ifnode, elifnodes, elsenode)

    def While(self) -> While:
        whilecond = self.R_Expr()
        log.debug(f"While condition located: {whilecond}")
        block = []
        if re.match(r";", self.program[self.pc]) is not None:
            # else
            self.eat(r";")
        else:
            self.eat(r"\{")
            self.Statement_Block(end_char = r"\}", block=block)
        whilenode = While(whilecond, Block(block))
        return whilenode
    
    def Return(self):
        match = re.match(r"return[\s]", self.program[self.pc:])
        if match is not None:
            match = match.group()
            self.eat(num_to_jump=len(match))
            expr = self.R_Expr()
            self.eat(r";")
            return Return(expr)

    def Typecase(self):
        if re.match(r"typecase\s", self.program[self.pc:]):
            self.eat(num_to_jump=8)
            test = self.R_Expr()
            log.debug(f"test = {test}")

            self.eat(r"\{")
            typecase = Typecase(test)
            while re.match(r"\}", self.program[self.pc:]) is None:
                check = self.ident()
                self.eat(r":")
                classtype = self.ident()
                self.eat(r"\{")
                block = []
                self.Statement_Block(r"\}", block)
                typecase.add_case(TypecaseCase(check, classtype, Block(block)))
            self.eat(r"\}")
            return typecase
        else:
            self.error("???????????")

    def Statement(self, nested: list = None):
        """
        if/elif/else, return, typecase, other statements
        """
        if nested is None:
            block = ParseTree.statements
        else:
            block = nested
        self.check_comment()

        # check typecase
        if re.match(r"typecase\s", self.program[self.pc:]):
            node = self.Typecase()
            block.append(node)
            log.info(node)
            return


        # check return
        if re.match(r"return\s", self.program[self.pc:]):
            node = self.Return()
            block.append(node)
            self.state = ParseTree.RETURN
            log.info(f"{node}")
            return

        # check if
        if re.match(r"if[\s\(]", self.program[self.pc:]):
            node = self.Conditional()
            block.append(node)
            log.info(f"{node}")
            return
        
        # check while
        elif re.match(r"while[\s\(]", self.program[self.pc:]):
            self.eat("", num_to_jump=5)
            node = self.While()
            block.append(node)
            log.info(f"{node}")
            return
        
        else:
            node = self.L_Expr()
            block.append(node)

            self.eat(r";")
        
        log.info(node)
        return
    
    def Statement_Block(self, end_char = None, block = None):
        log.info(f"Statement Block:\n-----------------")
        if end_char is None:
            while self.pc < self.len and self.state != ParseTree.RETURN:
                # on return, stop parsing
                self.Statement()
        else:
            while self.pc < self.len and re.match(end_char, self.program[self.pc:]) is None:
                if re.match(r"def", self.program[self.pc:]):
                    log.info("------------------")
                    return
                self.Statement(block)
            self.eat(end_char)
        log.info("------------------")
        return
    
    def Args(self):
        args = []
        if re.match(r"\(", self.program[self.pc]) is not None:
            self.eat(r"\(", 1)
        while re.match(r"\)", self.program[self.pc]) is None:
            name = self.ident()
            self.eat(r":")
            tpe = self.ident()
            args.append((name, tpe))
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

            # args on constructor is ok here
            # get args
            self.eat(r"\(", 1)
            args = self.Args()
            self.eat(r"\)", 1)

            # get return type
            self.eat(r":", 1)
            ret = self.ident()
            self.eat(r"\{", 1)

            # parse statements
            block = []
            self.Statement_Block(end_char = r"\}", block=block)
            if self.state != ParseTree.RETURN:
                block.append(Return(None))
            method = Method(name, args, ret, Block(block))
            log.info(f"Parsed {method}")
            # return
            return method
        else:
            # this should never never happen
            self.error(f"Error: attempted method parsing at {self.program[self.pc + 12]}")

    def ClassBody(self):
        # classbody is a sequence of statements followed by a sequence of method definitions
        block = []
        self.Statement_Block(end_char=r"\}", block=block)
        body = ClassBody(Block(block))

        log.debug(f"Statement block: {body.statements}")
        log.debug(f"finished statements, looking for method call at {self.program[self.pc:self.pc + 12]}")

        self.state = ParseTree.NORMAL
        while self.pc < self.len and re.match(r"def", self.program[self.pc:]) is not None:
            log.debug("Found a new method!")
            body.add_method(self.Method())
        self.eat(r"\}")
        log.info(f"ClassBody: {body}")
        return body
    
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

        # Optionally, new class can extend old class
        match = re.match(r"extends", self.program[self.pc:])
        if match is not None:
            self.eat(r"extends", len("extends"))
            parent = self.ident()
            log.debug(f"new class {classname} extending {parent}")
        else:
            parent = "Obj"
            log.debug(f"no parent given, new class {classname} inheriting Obj")
        self.eat(r"\{")

        self.state = ParseTree.CLASS
        new_class = Class(classname, args, None, parent)
        log.info(f"Parsing {new_class}\n--------------")

        new_class.set_body(self.ClassBody())

        log.debug(f"{new_class}")
        log.info(f"Successfully parsed {new_class}\n-------------------")
        return
    
    def Parse(self):
        # evaluate 0 or more class statements
        while self.pc < self.len and re.match(r"class", self.program[self.pc:]) is not None:
            self.Class()
        
        log.debug("Finished parsing class definitions - looking for statements...")
        log.debug(f"Current position: {self.program[self.pc:self.pc + 12]}")
        self.state = ParseTree.NORMAL
        # followed by a statement block
        # check that global statement block is still empty
        assert(ParseTree.statements == [])
        self.Statement_Block()

def main():
    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "ex.qk"
    # read quack

    path = ""
    out_file = file.split(".")[0]
    if file.startswith("tests/"):
        path = "tests/"
        out_file = file.split("/")[1].split(".")[0]

    out_file = out_file[0].upper() + out_file[1:]

    program = ""

    with open(file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if (line == "\n"):
                continue
            else:
                program += line

    tree = ParseTree(program)
    tree.Parse()

    for c in ParseTree.classes:
        Class.classes[c].evaluate()
        if c == out_file:
            out_file = "Main"

    Obj.ASM_FILE = f"{out_file}.asm"

    try:
        open(Obj.ASM_FILE, "x")
    except FileExistsError:
        os.remove(Obj.ASM_FILE)

    # f = open(Obj.ASM_FILE, "w+")
    # # write header information
    # print(f".class {out_file}:Obj", file=f)
    # print(".method $constructor", file=f, end="")

    # locals = ASTNode.get_locals()
    # if locals != f"":
    #     print(f"\t.local {locals}", file=f, end="")
    
    # print("\n\tenter", file=f)
    # f.close()

    log.info("Walking ASTNode Tree:")

    b = Block(ParseTree.statements)

    c = Class(out_file, [], ClassBody(b), "Obj", main=True)
    c.evaluate()

    # log.debug(f"End of block\n{ASTNode.buffer}*")

    log.debug("done")

if __name__ == "__main__":
    main()