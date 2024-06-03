import warnings
import logging as log

log.basicConfig(level=log.INFO)

TYPE, SYNTAX = range(2)

def ASTError(which: int, msg: str):
    if which == TYPE:
        raise TypeError(f"ASTError: " + msg)
    elif which == SYNTAX:
        raise SyntaxError(f"ASTError: " + msg)
    exit(1)

class Obj():
    """
    Main Object class for Quack. This shouldn't ever be called directly.
    """
    ASM_FILE = "out.asm"

    methods: list[str] = ["string", "print", "equals"]

    def __init__(self, value: None):
        self.val = value
        self.type = "Obj"

    def get_type(self) -> str:
        return self.type

    def check(self):
        return self.type

    def evaluate(self):
        # with open(Obj.ASM_FILE, "a+") as f:
        #     print(f"\tconst {self.val}", file=f)
        # f.close()
        ASTNode.buffer += f"\tconst {self.val}\n"
        return self.type

    def __str__(self):
        return f"{self.type}: {self.val}"
    
class Int(Obj):
    methods: list[str] = ["string", "print", "equals", "plus", "minus", "times", "divide", "less"]

    def __init__(self, value: int):
        super().__init__(value)
        self.val = value
        self.type = "Int"

    def evaluate(self):
        if self.val < 0:
            # print(f"\tconst 0", file=f)
            # print(f"\tconst {abs(self.val)}", file=f)
            # print(f"\tcall Int:minus", file=f)
            ASTNode.buffer += f"\tconst 0\n\tconst {abs(self.val)}\n\tcall Int:minus\n"
        else:
            # print(f"\tconst {self.val}", file=f)
            ASTNode.buffer += f"\tconst {self.val}\n"
        return self.type


class String(Obj):
    # list of methods for the String class
    methods: list[str] = ["print"]

    def __init__(self, value: str):
        super().__init__(value)
        self.val = value
        self.type = "String"

class Bool(Obj):
    # list of methods for the Bool class
    methods: list[str] = ["print", "string", "and", "or"]

    def __init__(self, value: str):
        super().__init__(value)
        self.val = value
        if self.val == "true":
            self.true_false = True
        else:
            self.true_false = False
        self.type = "Bool"

    def evaluate(self):
        # with open(Obj.ASM_FILE, "a") as f:
        #     print(f"\tconst {self.val}", file=f)
        # f.close()
        ASTNode.buffer += f"\tconst {self.val}\n"
        return self.type

class Nothing(Obj):
    
    methods: list[str] = []

    def __init__(self):
        self.val = None
        self.type = "Nothing"

    def __str__(self):
        return self.type
    
    def evaluate(self):
        # with open(Obj.ASM_FILE, "a") as f:
        #     print(f"\tconst none", file=f)
        # f.close()
        ASTNode.buffer += f"\tconst none\n"
        return self.type

class Variable(Obj):
    def __init__(self, var_name: str, decl_type: str = None):
        self.name = var_name
        self.type = decl_type

    def get_type(self) -> str:
        return self.type

    def assign(self, type: str = None):
        if type is not None:
            self.type = type
        else:
            warnings.warn(f"Assigning type {None} to variable {self.name}")

    def __str__(self):
        return f"Variable: {self.type} {self.name}"
    
    def store(self) -> None:
        log.info(f"{self}")
        ASTNode.add_var(self.name, self.type)
        # with open(Obj.ASM_FILE, "a") as f:
        #     print(f"\tstore {self.name}", file=f)
        # f.close()
        ASTNode.buffer += f"\tstore {self.name}\n"
        return self.type

    def check(self):
        # check that the variable exists on evaluate()
        tpe = ASTNode.locate_var(self.name) 
        if tpe is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.name}")

    def evaluate(self) -> None:
        self.check()
        ASTNode.buffer += f"\tload {self.name}\n"
        return self.type


"""
Base class. Mainly used for generating loop/cond labels
"""
class ASTNode():
    if_stmts = 0
    elif_stmts = 0
    else_stmts = 0
    loops = 0
    block_label = 0
    boolcomp_label = 0
    typecase_label = 0
    typecase_gen_label = 0

    """
    scope & block_level contain the live set information for variables
    each block has a level, the live set is the union of the current level and 
    all previous levels up to 0. When a block ends, it is popped off the scope.

    Variable name conflicts prioritize the more local scope
    """
    scope: dict[str: str] = {}

    args: list[str] = {}
    block_level = 0

    buffer = f""
    program = f""

    parsing_class = None

    def __init__(self):
        self.ret_type = "Nothing"
    
    def gen_if_label():
        ret = f"{ASTNode.if_stmts}"
        ASTNode.if_stmts += 1
        return ret
    
    def gen_elif_label():
        ret = f"{ASTNode.elif_stmts}"
        ASTNode.elif_stmts += 1
        return ret
    
    def gen_else_label():
        ret = f"{ASTNode.else_stmts}"
        ASTNode.else_stmts += 1
        return ret
    
    def gen_loop_label():
        ret = f"{ASTNode.loops}"
        ASTNode.loops += 1
        return ret
    
    def fetch_and_update_block_label():
        ret = f"block{ASTNode.block_label}"
        ASTNode.block_label += 1
        return ret
    
    def gen_boolcomp_label():
        ret = f"cond{ASTNode.boolcomp_label}"
        ASTNode.boolcomp_label += 1
        return ret
    
    def gen_typecase_label():
        ret = f"{ASTNode.typecase_label}"
        ASTNode.typecase_label += 1
        return ret
    
    def gen_typecase_gen_label():
        ret = f"{ASTNode.typecase_gen_label}"
        ASTNode.typecase_gen_label += 1
        return ret
    
    def locate_var(name) -> str:
        # log.info(f"{ASTNode.scope}")
        try:
            return ASTNode.scope[name]
        except:
            try:
                return ASTNode.args[name]
            except:
                return None
    
    def add_var(name, tpe) -> None:
        ASTNode.scope[name] = tpe

    def reset_variables():
        ASTNode.scope = {}
        ASTNode.args = {}
    
    def get_locals():
        vars = []
        ret = f""
        for v in list(ASTNode.scope.keys()):
            if v not in ASTNode.args:
                vars.append(v)
                ret += f",{v}"

        if ret != f"":
            return ret[1:]
        return f""
    
    def set_asm_file(f: str):
        Obj.ASM_FILE = f

        # clear the file
        file = open(f, "w+")
        file.close()

    def print_buffer():
        ASTNode.program += ASTNode.buffer
        ASTNode.buffer = f""

    def write():
        ASTNode.print_buffer()
        with open(Obj.ASM_FILE, "a+") as f:
            print(ASTNode.program, file=f, end="")
        f.close()
        ASTNode.program = f""

    def set_parse_class(name: str):
        ASTNode.parsing_class = name

"""
Block class: List of statements, to be evaluated in order.
Implementing a class allows the .evaluate() method to be defined, which is helpful.
"""
class Block(ASTNode):
    def __init__(self, statements: list[ASTNode | Obj]):
        # a block is just a list of statements
        # but this way allows the evaluate method to be implemented
        # which is useful
        self.statements = statements
    
    def __str__(self):
        # i am lazy
        retstr = f"Block: _"
        for s in self.statements:
            retstr += f", {s}"
        return retstr

    def evaluate(self):
        # evaluate the list of statements
        ret = "Nothing"
        for s in self.statements:
            ret = s.evaluate()

        # this should always return the value of the return statement
        # log.debug(f"End of block\n{ASTNode.buffer}")
        # ASTNode.print_buffer()

        return ret
    
class Expression(ASTNode):
    # expression node
    # operator maps to functions
    ops = {"+": "plus", "-": "minus", "*": "multiply", "/": "divide"}

    def __init__(self, left: ASTNode | Obj, right: ASTNode | Obj, op: str):
        self.left = left
        self.right = right
        # this is old but it works
        # give objects type prio over other nodes
        if isinstance(left, Obj):
            self.type = left.type
        elif isinstance(right, Obj):
            self.type = right.type
        else:
            self.type = "Nothing"
        
        if op in "+-*/":
            self.token = op
            self.op = Expression.ops[op]
        # this shouldn't ever happen
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")

    def check(self):
        # operands can be any type but have to be the same
        # worry about implementation in actual call
        if isinstance(self.left, str):
            left = ASTNode.locate_var(self.left)
            self.left = Variable(self.left, left)
        
        self.left.check()
        left = self.left.type

        if left is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.left}")

        if isinstance(self.right, str):
            right = ASTNode.locate_var(self.right)
            self.right = Variable(self.right, right)
        
        self.right.check()
        right = self.right.type

        if right is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.right}")

        # Also, because we changed when type checking and variable tracking happens, left.type and right.type may not be defined on initialization
        if left != right:
            ASTError(TYPE, f"Operands must have same type, not {left} and {right}.")
        else:
            # set self.type at this point
            self.type = left

        if self.type == "Int":
            return
        else:
            try:
                c = Class.classes[self.type]
                if self.op not in c.get_methods():
                    ASTError(SYNTAX, f"Method {self.token} ({self.op.upper()}) undefined for class {self.type}")
            except:
                ASTError(SYNTAX, f"Undefined class {self.type}.")

    def evaluate(self):
        self.check()

        self.left.evaluate()
        self.right.evaluate()

        ASTNode.buffer += f"\tcall {self.type}:{self.op}\n"
        return self.type

    def __str__(self):
        return f"Expression: ({self.left} {self.token} {self.right}), {self.type}"

class BoolComp(ASTNode):
    def __init__(self, left: Expression | Int, right: Expression | Int, op: str):
        # and/or

        self.left = left
        self.right = right
        self.type = "Bool"

        if op in ["and", "or"]:
            self.op = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def check(self):
        # check that both arguments are bools
        if isinstance(self.left, str):
            left = ASTNode.locate_var(self.left)
            self.left = Variable(self.left, left)
        else:
            left = self.left.type

        if left is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.left}")

        if isinstance(self.right, str):
            right = ASTNode.locate_var(self.right)
            self.right = Variable(self.right, right)
        else:
            right = self.right.type

        if right is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.right}")

        if left != "Bool" or right != "Bool":
            ASTError(TYPE, f"And/Or Comparison can only be executed for Boolean values, not {left}, {right}.")

    def __str__(self):
        return f"BoolComp: {self.left} {self.op} {self.right}"
    
    def eval_or(self) -> None:
        # generate label
        label = ASTNode.gen_boolcomp_label()

        # short circuit on first
        self.left.evaluate()
        # with open(Obj.ASM_FILE, "a+") as f:
        #     print(f"\tjump_if short{label}", file=f)
        # f.close()
        ASTNode.buffer += f"\tjump_if short{label}\n"
        # check second
        self.right.evaluate()
        ASTNode.buffer += f"\tjump {label}\nshort{label}:\n\tconst true\n\tjump {label}\n{label}:\n"

        # continue

    
    def eval_and(self):
        log.debug("and")
        # generate label
        label = ASTNode.gen_boolcomp_label()

        # short circuit on first
        self.left.evaluate()
        ASTNode.buffer += f"\tjump_ifnot short{label}\n"

        # check second
        self.right.evaluate()
        ASTNode.buffer += f"\tjump {label}\nshort{label}:\n\tconst false\n\tjump {label}\n{label}:\n"
        # continue

    def evaluate(self):
        self.check()
        if self.op == "or":
            self.eval_or()
        elif self.op == "and":
            self.eval_and()
        return self.type

class IntComp(ASTNode):
    def __init__(self, left: Expression | Int, right: Expression | Int, op: str):
        self.left = left
        self.right = right
        self.type = "Bool"

        self.eval_type = "Nothing"

        if op in [">", "<", "==", "<=", ">="]:
            self.op = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def __str__(self):
        return f"IntComp: {self.left} _{self.op}_ {self.right}, eval_type = {self.eval_type}"
    
    def check(self):
        if isinstance(self.left, str):
            left = ASTNode.locate_var(self.left)
            self.left = Variable(self.left, left)
        else:
            left = self.left.type

        if left is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.left}")

        if isinstance(self.right, str):
            right = ASTNode.locate_var(self.right)
            self.right = Variable(self.right, right)
        else:
            right = self.right.type

        if right is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.right}")

        if left != right:
            ASTError(TYPE, "Comparison can only be executed for same types.")
        else:
            self.eval_type = left
    
    def evaluate(self):
        self.check()

        # log.debug(f"\n{ASTNode.buffer}")

        # this is <, > - only need to check one thing
        if len(self.op) == 1:
            if self.op[0] == "<":
                self.right.evaluate()
                self.left.evaluate()
            else:
                self.left.evaluate()
                self.right.evaluate()
            ASTNode.buffer += f"\tcall {self.eval_type}:less\n"

        # if len = 2, either ==, which is one call..
        elif self.op == "==":
            self.left.evaluate()
            self.right.evaluate()
            ASTNode.buffer += f"\tcall {self.eval_type}:equals\n"

        # .. or <=, >=, which are combined into "less than or equals" with a boolean or
        elif len(self.op) == 2:
            op = BoolComp(IntComp(self.left, self.right, self.op[0]), IntComp(self.left, self.right, "=="), "or")
            op.evaluate()

        else:
            ASTError(SYNTAX, f"Error in parsing integer comparison operation. ")

# TODO: make it so that not true will work
class Not(ASTNode):
    def __init__(self, expr: IntComp | Bool):
        if isinstance(expr, IntComp):
            self.expr = IntComp(expr.right, expr.left, expr.op)
        elif isinstance(expr, BoolComp):
            self.expr = BoolComp(expr.right, expr.left, expr.op)
        else:
            ASTError(TYPE, "Not can only be applied to boolean expressions.")
        self.type = "Bool"

    def __str__(self):
        return f"Not: {self.expr}"

    def evaluate(self):
        # reverse control flow
        self.expr.evaluate()

class Assign(ASTNode):
    def __init__(self, var: Variable | str, val: Obj | ASTNode, declared_type: int = None):
        self.val = val
        if declared_type is not None:
            self.type = declared_type
        else:
            self.type = "Nothing"
        
        if isinstance(var, str):
            vt = ASTNode.locate_var(var)
            if vt is None:
                self.var = Variable(var, self.type)
            else:
                self.var = Variable(var, vt)
        else:
            self.var = var
        
        self.static = True
        if declared_type is None:
            self.static = False

    def check(self):
        # If we assigned a variable to another variable, 
        # Locate it in the current live set.
        val = self.val
        
        if isinstance(self.val, str):
            val = ASTNode.locate_var(self.val)
            self.val = Variable(self.val, val)
        elif isinstance(self.val, Field):
            val = Class.classes[self.val.belongs].get_field(self.val.field)

        self.val.check()
        val = self.val.type

        if val is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.val}")

        if val != self.var.type and self.var.type != "Nothing":
            if self.static or isinstance(self.var, Field):
                ASTError(TYPE, f"Cannot assign type {val} to variable or field of declared type {self.type}")
            warnings.warn(f"Reassigning variable {self.var} to type {val}")
            self.var.type = val
        else:
            self.var.type = val
        self.type = val
        
    def set_type(self, t):
        self.type = t
        self.var.type = t

    def __str__(self):
        return f"Assign: {self.var}, {self.val} <{self.type}>"
    
    def evaluate(self):
        self.check()
        self.val.evaluate()
        self.var.store()
        log.info(f"{self}")

class Return(ASTNode):
    def __init__(self, ret: Obj | ASTNode):
        self.ret = ret
        self.type = "Nothing"
    
    def __str__(self):
        return f"Return: {self.ret}"
    
    def evaluate(self):
        if self.ret is not None:
            self.ret.evaluate()
        
        log.info(f"{self}")

        ASTNode.buffer += f"\treturn "
        if self.ret is None:
            return "Nothing"
        return self.ret.type

# TODO: flow-sensitive variable exist analysis
class IfNode(ASTNode):
    def __init__(self, cond: IntComp | BoolComp, block: Block):
        self.statement = block
        self.cond = cond

    def __str__(self):
        return f"If: {self.cond}, [{self.statement}]"
    
    def check(self):
        if self.cond.type != "Bool":
            ASTError(TYPE, f"Conditional statement {self.cond} must be a bool!")
    
    def evaluate(self):
        self.check()
        self.statement.evaluate()
        return "Bool"

class ElifNode(ASTNode):
    def __init__(self, cond: Expression, block: Block):
        self.statement = block
        self.cond = cond

    def check(self):
        if self.cond.type != "Bool":
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"Elif: {self.cond} [{self.statement}]"
    
    def evaluate(self):
        self.check()
        self.statement.evaluate()
        return "Bool"
    
class ElseNode(ASTNode):
    def __init__(self, block: Block):
        self.statement = block

    def __str__(self):
        return f"Else: [{self.statement}]"
    
    def evaluate(self):
        self.statement.evaluate()
        return "Bool"

class Conditional(ASTNode):
    def __init__(self, ifnode: IfNode, elifnode: list[ElifNode], elsenode: ElseNode):
        self.ifnode = ifnode
        self.elifnode = elifnode
        self.elsenode = elsenode

        # this should never happen
        if ifnode is None:
            ASTError(SYNTAX, "No if statement provided.")

    def __str__(self):
        return f"Conditional: if ({self.ifnode.cond}); elif ({self.elifnode}); else ({self.elsenode})"

    def evaluate(self):
        block = ASTNode.fetch_and_update_block_label()
        iflabel = ASTNode.gen_if_label()
        self.ifnode.cond.evaluate()

        # with open(Obj.ASM_FILE, "a+") as f:
        #     print(f"\tjump_if if_clause{iflabel}", file=f)
        # f.close()
        ASTNode.buffer += f"\tjump_if if_clause{iflabel}\n"
        eliflabels = []
        if self.elifnode is not None:
            for elf in self.elifnode:
                eliflabels.append(ASTNode.gen_elif_label())
                elf.cond.evaluate()
                # with open(Obj.ASM_FILE, "a+") as f:
                #     print(f"\tjump_if elif_clause{eliflabels[-1]}", file=f)
                # f.close()
                ASTNode.buffer += f"\tjump_if elif_clause{eliflabels[-1]}\n"

        if self.elsenode is not None:
            self.elsenode.evaluate()
            # with open(Obj.ASM_FILE, "a+") as f:
            #     print(f"\tjump {block}", file=f)
            # f.close()
            ASTNode.buffer += f"\tjump {block}\n"
        
        # with open(Obj.ASM_FILE, "a+") as f:
        #     print(f"if_clause{iflabel}:", file=f)
        # f.close()
        ASTNode.buffer += f"if_clause{iflabel}:\n"
        self.ifnode.evaluate()
        # with open(Obj.ASM_FILE, "a+") as f:
        #     print(f"\tjump {block}", file=f)
        # f.close()
        ASTNode.buffer += f"\tjump {block}\n"

        for label, elf in zip(eliflabels, self.elifnode):
            # with open(Obj.ASM_FILE, "a+") as f:
            #     print(f"elif_clause{label}:", file=f)
            # f.close()
            ASTNode.buffer += f"elif_clause{label}:\n"
            elf.evaluate()
            # with open(Obj.ASM_FILE, "a+") as f:
            #     print(f"\tjump {block}", file=f)
            # f.close()
            ASTNode.buffer += f"jump {block}\n"

        # with open(Obj.ASM_FILE, "a+") as f:
        #     print(f"{block}:", file=f)
        # f.close()
        ASTNode.buffer += f"{block}:\n"

class While(ASTNode):
    def __init__(self, cond: IntComp | BoolComp, block: Block):
        self.statement = block
        self.cond = cond

    def check(self):
        if self.cond.type != "Bool":
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"While: {self.cond} [{self.statement}]"
    
    def evaluate(self):
        self.check()
        loop = ASTNode.gen_loop_label()
        # with open(Obj.ASM_FILE, "a+") as f:
        #     # print(f"loop{loop}:", file=f)
        #     print(f"\tjump startl{loop}", file=f)
        #     print(f"startl{loop}:", file=f)
        # f.close()
        ASTNode.buffer += f"\tjump startl{loop}\nstartl{loop}:\n"
        self.cond = Not(self.cond)
        self.cond.evaluate()
        # with open(Obj.ASM_FILE, "a+") as f:
        #     # print(f"\tjump_if end_loop{loop}",  file=f)
        #     print(f"\tjump_if endl{loop}", file=f)
        # f.close()
        ASTNode.buffer += f"\tjump_if endl{loop}\n"
        self.statement.evaluate()
        # with open(Obj.ASM_FILE, "a+") as f:
        #     print(f"\tjump startl{loop}", file=f)
        #     print(f"endl{loop}:", file=f)
        # f.close()
        ASTNode.buffer += f"\tjump startl{loop}\nendl{loop}:\n"

class Field(ASTNode):
    # field access of a class instance
    def __init__(self, belongs: Obj | ASTNode = None, field: str | Variable = None):
        # field accessing
        self.field = field
        
        # parent
        self.belongs = belongs

        self.type = "Nothing"

        if isinstance(field, Variable):
            self.type = field.type

    def __str__(self):
        return f"Field: {self.belongs}.{self.field}, <{self.type}>"
    
    def check(self):
        # check that belongs is initialized
        if self.belongs == "this":
            val = ASTNode.parsing_class
        else:
            val = ASTNode.locate_var(self.belongs)

        if val is None:
            ASTError(SYNTAX, f"Uninitialized variable {self.belongs}")
        
        # if it is, check that field is in class type
        else:
            try:
                c = Class.classes[val]
                val = c.get_field(self.field)
            except:
                ASTError(SYNTAX, f"Class {val} does not exist. (Or does not have fields if builtin)")
        # set type
        self.type = val
        
    def evaluate(self):
        self.check()
        if self.belongs == "this":
            this = "$"
            ASTNode.buffer += f"\tload {this}\n\tload_field {this}:{self.field}\n"
        else:
            this = ASTNode.locate_var(self.belongs)
            if this == ASTNode.parsing_class:
                this = "$"
            ASTNode.buffer += f"\tload {self.belongs}\n\tload_field {this}:{self.field}\n"
        return self.type

    def store(self):
        if self.belongs == "this":
            # add new field to the current parsing class
            Class.classes[ASTNode.parsing_class].add_field(self.field, self.type)
            this = "$"
        else:
            self.check()
            this = self.belongs
            if self.belongs == ASTNode.parsing_class:
                this = "$"

        ASTNode.buffer += f"\tload {this}\n\tstore_field {this}:{self.field}\n"
        return self.type

# formal parameters for a method
class Params(ASTNode):
    def __init__(self, params: list[(str, str | int)] = []):
        self.params = params
    
    def add_param(self, new_param: tuple[str, str | int]):
        """
        Add a new argument to a method or class signature
        takes a tuple (name, type), where name is the variable name and type is str of class name
        """
        # skip this - reference to inherent class variable
        if new_param[0] != "this":
            self.params.append(new_param)

    def get_param_names(self):
        if self.params != []:
            f = f"{self.params[0][0]}"
            for p in self.params[1:]:
                f += f",{p[0]}"
            return f
        return f""
    
    def set_args(self):
        ASTNode.args = {p[0]: p[1] for p in self.params}
    
    def get_params(self):
        p = []
        for param in self.params:
            p.append(param[1])
        return p

    def __str__(self):
        f = f""
        for p in self.params:
            f = f + f"{p[0]}: {p[1]},"
        return f[0:-1]
    

class Method(ASTNode):
    def __init__(self, name: str, args: Params | list, ret: int | str, block: Block):
        self.name = name
        if isinstance(args, list):
            args = Params(args)

        self.args = args
        # return type of method
        self.type = ret
        # statements
        self.block = block

        self.locals: dict[str: str | int] = {}

        self.builtin = False

        if self.name in ["PRINT", "EQUALS", "STRING", "LESS", "PLUS", "MINUS", "DIVIDE", "MULTIPLY"]:
            self.builtin = True

    def add_local(self, var: Variable) -> None:
        self.locals[var.name] = var

    def get_locals(self) -> str | None:
        if len(self.locals.keys()) <= 1:
            return None
        f = f""
        for l in self.locals.keys():
            if l != "this":
                f += f",{l}"
        return f[1:]

    def __str__(self):
        return f"Method: {self.name}({self.args}) -> {self.type}"
    
    def check(self):
        if self.builtin:
            self.name = self.name.lower()
    
    def evaluate(self):
        self.check()
        log.info(f"{self}")
        ASTNode.buffer += f"\n.method {self.name}\n"

        self.args.set_args()
        args = self.args.get_param_names()
        if args != f"":
            ASTNode.buffer += f".args {args}\n"
        # ASTNode.print_buffer()

        ASTNode.print_buffer()

        ret = self.block.evaluate()

        temp_buffer = f""
        # do local variables at this point

        locals = ASTNode.get_locals()
        if locals != f"":
            temp_buffer += f"\t.local {locals}\n"

        temp_buffer += f"\tenter\n"

        # workaround that hopefully doesn't backfire - it's a very specific stack problem, basically if method returns nothing and the last statement in a method isn't loading a thing, the stack gets double-popped and messes up. 
        if self.type == "Nothing" or self.name == "print":
            ASTNode.buffer += f"\tload $\n"

        if not isinstance(self.block.statements[-1], Return):
            ASTNode.buffer += f"\treturn "
            
        ASTNode.buffer += f"{len(self.args.params)}\n"

        ASTNode.buffer = temp_buffer + ASTNode.buffer

        if ret is None and self.type == "Nothing":
            return
        if ret != self.type:
            ASTError(TYPE, f"Return value of {ret} does not matched declared return value {self.type}")


        ASTNode.print_buffer()
        ASTNode.reset_variables()

class ClassBody(ASTNode):
    def __init__(self, statements: Block, methods: list[Method] = []):
        self.statements = statements
        self.methods = methods

    def __str__(self):
        f = f"Init: {self.statements}\nMethods: _"
        for m in self.methods:
            f += f", {m}"
        return f
    
    def add_method(self, m: Method):
        self.methods.append(m)

    def get_methods(self):
        return {m.name: m for m in self.methods}

    def evaluate(self, l, main):
        ASTNode.buffer += f"\tenter\n"
        self.statements.evaluate()

        if not main:
            ASTNode.buffer += f"\tload $\n"
        ASTNode.buffer += f"\treturn {l}\n"
        ASTNode.print_buffer()

        for method in self.methods:
            method.evaluate()

class Class(ASTNode):
    # list of user-defined classes
    # name of class : class
    classes: dict[str: ASTNode] = {}

    def __init__(self, classname: str, constructor_args: Params | list = None, class_body: ClassBody = None, parent: str = "Obj", main=False):
        self.name = classname
        self.main = main

        if isinstance(constructor_args, list):
            constructor_args = Params(constructor_args)

        self.params = constructor_args
        self.class_body = class_body
        self.parent = parent
        
        self.fields: dict[str: type] = {}

        Class.classes[self.name] = self

        ASTNode.set_parse_class(self.name)

    def __str__(self):
        return f"Class: {self.name} ({self.params}) -> {self.parent}\nFields: {self.fields}\nMethods: {self.get_method_names()}"
    
    def get_method_names(self):
        m = []
        if self.class_body is not None:
            for method in self.class_body.methods:
                m.append(method.name)
        return m
    
    def get_params(self):
        return self.params.get_params()
    
    def set_body(self, body: ClassBody):
        self.class_body = body

    def get_methods(self):
        return self.class_body.get_methods()
    
    def add_field(self, name: str, type: int | str):
        self.fields[name] = type
    
    def get_field(self, name):
        try:
            return self.fields[name]
        except:
            ASTError(f"Field {name} does not exist for class {self.name}")

    def check(self):
        # check that the parent is a valid class
        # all other type checks happen later
        try:
            c = Class.classes[self.parent]
        except:
            if self.parent not in ["Int", "Bool", "Obj", "String", "Nothing"]:
                ASTError(TYPE, f"Parent class {self.parent} is undefined.")

    def evaluate(self):
        self.check()
        # check if it inherits a builtin class or a new class
        inherit = self.parent

        ASTNode.set_asm_file(f"{self.name}.asm")

        ASTNode.buffer += f".class {self.name}:{inherit}\n"

        ASTNode.write()

        ASTNode.args = {p[0]: p[1] for p in self.params.params}

        self.class_body.evaluate(len(self.get_params()), self.main)

        temp_buffer = f""
        for f in self.fields.keys():
            temp_buffer += f".field {f}\n"
        
        for m in self.class_body.methods:
            temp_buffer += f".method {m.name} forward\n"
        
        temp_buffer += f".method $constructor\n"
        if self.params.params != []:
            temp_buffer += f".args\t"
            temp_buffer += f"{self.params.get_param_names()}\n"

        locals = ASTNode.get_locals()
        if locals != f"":
            temp_buffer += f".local\t{locals}\n"

        ASTNode.program = temp_buffer + ASTNode.program

        log.info(f"{self}")

        ASTNode.write()

        # return class name as type
        return self.name

class UserClassInstance(ASTNode):
    def __init__(self, class_type: str, constructor_args: list[Obj]):
        self.type = class_type
        self.args = constructor_args
    
    def check(self):
        try:
            c = Class.classes[self.type]
        except:
            ASTError(SYNTAX, f"Class <{self.type}> is undefined.")

        if len(c.get_params()) == len(self.args) and c.get_params() != []:
            for a, c in zip(self.args, c.get_params()):
                a.check()
                if a.type != c:
                    ASTError(TYPE, f"Type {a.type} does not match constructor type {c}")
        elif len(self.args) != 0:
            ASTError(SYNTAX, f"{self.type} constructor takes {len(c.get_params())} arguments but {len(self.args)} were given.")

    def __str__(self):
        return f"User class instance: {self.type}({self.args})"
    
    def evaluate(self):
        self.check()
        for arg in self.args:
            arg.evaluate()
        # with open(Obj.ASM_FILE, "a") as f:
        #     print(f"\tnew {self.type}\n\tcall {self.type}:$constructor", file=f)
        # f.close()
        t = self.type
        if self.type == ASTNode.parsing_class:
            t = "$"
        ASTNode.buffer += f"\tnew {t}\n\tcall {t}:$constructor\n"

class TypecaseCase(ASTNode):
    def __init__(self, test, test_type, statement: Block):
        self.name = test
        self.type = test_type
        self.statements = statement
    
    def __str__(self):
        return f"{self.name} : {self.type} [{self.statements}]"
    
    def evaluate_check(self, label):
        t = self.type
        # with open(Obj.ASM_FILE, "a") as f:
        #     print(f"\tis_instance {t}", file=f)
        #     print(f"\tjump_if it_is{label}", file=f)
        # f.close()
        ASTNode.buffer += f"\tis_instance {t}\n\tjump_if it_is{label}\n"

    def evaluate_block(self, label, tl):
        ASTNode.buffer += f"it_is{label}:\n"
        self.statements.evaluate()
        ASTNode.buffer += f"\tjump next{tl}\n"

class Typecase(ASTNode):
    def __init__(self, test: Obj | ASTNode, cases: list[TypecaseCase] = []):
        self.test = test
        self.cases = cases

    def add_case(self, new_case: TypecaseCase):
        self.cases.append(new_case)

    def __str__(self):
        f = f"typecase {self.test}: "
        for case in self.cases:
            f += f"{case}, "
        return f
    
    def evaluate(self):
        labels = []
        tl = ASTNode.gen_typecase_gen_label()
        for c in self.cases:
            label = ASTNode.gen_typecase_label()
            labels.append(label)
            # with open(Obj.ASM_FILE, "a") as f:
            #     print(f"\tload {self.test}", file=f)
            # f.close()
            ASTNode.buffer += f"\tload {self.test}\n"
            c.evaluate_check(label)
        
        for c, l in zip(self.cases, labels):
            c.evaluate_block(l, tl)
        
        ASTNode.buffer += f"next{tl}:\n"

class Call(ASTNode):
    def __init__(self, var: Obj | ASTNode = None, method: str = None, args: Params = None):
        self.var = var
        self.type = "Nothing"
        self.calling_type = "Nothing"

        self.args = args

        self.method = method

        self.type = "Nothing"

    def check(self):
        if isinstance(self.var, str):
            tpe = ASTNode.locate_var(self.var)
            if tpe is None:
                ASTError(SYNTAX, f"Cannot call method {self.method} on uninitialized variable {self.var}")

            self.var = Variable(self.var, tpe)

        self.var.check()
        self.calling_type = self.var.type

        self.check_method()
        self.check_args()

    def check_args(self):
        # builtins which take no arguments
        if self.method in ["print", "string"]:
            if self.args is not None and len(self.args) != 0:
                ASTError(SYNTAX, f"Method {self.method} takes 0 arguments, {len(self.args)} given.")
        elif self.method in ["equals", "less", "add", "minus", "times", "divide"]:
            p = self.args
            if self.args is None or len(p) > 1 or len(p) == 0:
                ASTError(SYNTAX, f"Method {self.method} takes 1 arguments, {len(self.args.get_params())} given.")
            elif p[0].type != self.calling_type:
                ASTError(TYPE, f"Argument type {p[0].type} must match calling type {self.calling_type} for method {self.method}.")
        
    def check_method(self):
        if self.calling_type not in ["Int", "String", "Obj", "Bool", "Nothing"]:
            ms = Class.classes[self.calling_type].get_methods()
            try:
                self.type = ms[self.method].type
            except:
                self.calling_type = Class.classes[self.calling_type].parent
                self.check_method()
                return
        else:
            if self.calling_type == "Int":
                if self.method in ["less", "equals"]:
                    self.type = "Bool"
                elif self.method in ["plus", "minus", "times", "divide"]:
                    self.type = "Int"
            else:
                if self.method in ["equals"]:
                    self.type = "Bool"
                elif self.method in ["string"]:
                    self.type = "String"

    def assign_var(self, expr: Obj | ASTNode):
        self.var = expr
        self.calling_type = expr.type

    def __str__(self):
        return f"Call: {self.var}.{self.method}({self.args}), ret_type={self.type}"
    
    def evaluate(self) -> None:
        """
        Eventually include type checking in this
        """
        self.check()
        log.info(f"{self}")

        calling = ""
            
        if self.calling_type == "Int":
            if self.method not in Int.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.calling_type}")
            calling = "Int"
        elif self.calling_type == "Obj":
            if self.method not in Obj.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.calling_type}")
            calling = "Obj"
        elif self.calling_type == "Bool":
            if self.method not in Bool.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.calling_type}")
            calling = "Bool"
        elif self.calling_type == "String":
            if self.method not in String.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.calling_type}")
            calling = "String"
        elif self.calling_type == "Nothing":
            raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.calling_type}")
        elif isinstance(self.calling_type, str):
            if self.method not in Class.classes[self.calling_type].get_method_names():
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.calling_type}")
            calling = self.calling_type
        
        for arg in self.args:
            arg.evaluate()

        self.var.evaluate()

        ASTNode.buffer += f"\tcall {calling}:{self.method}\n"

        # if method returns nothing, pop result
        # if self.type == "Nothing":
        #     ASTNode.buffer += f"\tpop\n"

        # log.debug(f"-----------\n{ASTNode.buffer}*\n------------")
        return self.type