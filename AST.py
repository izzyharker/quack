from quack_builtins import *

TYPE, SYNTAX = range(2)

def ASTError(which: int, msg: str):
    if which == TYPE:
        raise TypeError(msg)
    elif which == SYNTAX:
        raise SyntaxError(msg)
    exit(1)

class ASTNode():
    if_stmts = 0
    elif_stmts = 0
    else_stmts = 0
    loops = 0
    block_label = 0
    boolcomp_label = 0

    def __init__(self):
        self.type = NOTHING
    
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
        ret = f"cont{ASTNode.boolcomp_label}"
        ASTNode.boolcomp_label += 1
        return ret

class Block(ASTNode):
    def __init__(self, statements: list[ASTNode | Obj]):
        self.statements = statements
    
    def __str__(self):
        retstr = f"Block: _"
        for s in self.statements:
            retstr += f", {s}"
        return retstr

    def evaluate(self):
        for s in self.statements:
            s.evaluate()

class Expression(ASTNode):
    # expression node
    ops = {"+": "plus", "-": "minus", "*": "multiply", "/": "divide"}

    def __init__(self, left: ASTNode | Obj, right: ASTNode | Obj, op: str):
        self.left = left
        self.right = right
        if isinstance(left, Obj):
            self.type = left.type
        elif isinstance(right, Obj):
            self.type = right.type
        else:
            self.type = left.type

        if left.type != right.type:
            ASTError(TYPE, f"Operands must have same type, not {node_types[left.type]} and {node_types[right.type]}.")
        
        if op in "+-*/":
            self.token = op
            self.op = Expression.ops[op]
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")

    def evaluate(self):
        self.left.evaluate()
        self.right.evaluate()

        # print to file
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tcall {node_types[self.type]}:{self.op}", file=f)
        f.close()
        # print(f"\tcall Int:{Operator.ops[self.op]}")
        
        pass

    def __str__(self):
        return f"Expression: ({self.left} {self.token} {self.right})"

class BoolComp(ASTNode):
    def __init__(self, left: Expression | Int, right: Expression | Int, op: str):
        self.left = left
        self.right = right
        self.type = BOOL

        if right.type != BOOL or left.type != BOOL:
            ASTError(TYPE, f"Comparison can only be executed for Boolean values, not {node_types[self.left.type]}, {node_types[self.right.type]}.")

        if op in ["and", "or"]:
            self.op = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def __str__(self):
        return f"BoolComp: {self.left} {self.op} {self.right}"
    
    def eval_or(self) -> None:
        # generate label
        label = ASTNode.gen_boolcomp_label()

        # short circuit on first
        self.left.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tjump_if short{label}", file=f)
        f.close()
        # check second
        self.right.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tjump {label}", file=f)
            print(f"short{label}:", file=f)
            print(f"\tconst true", file=f)
            print(f"\tjump {label}", file=f)
            print(f"{label}:", file=f)
        f.close()
        # continue
    
    def eval_and(self):
        # generate label
        label = ASTNode.gen_boolcomp_label()

        # short circuit on first
        self.left.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tjump_ifnot short{label}", file=f)
        f.close()
        # check second
        self.right.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tjump {label}", file=f)
            print(f"short{label}:", file=f)
            print(f"\tconst false", file=f)
            print(f"\tjump {label}", file=f)
            print(f"{label}:", file=f)
        f.close()
        # continue

    def evaluate(self):
        if self.op == "or":
            self.eval_or()
        elif self.op == "and":
            self.eval_and()

# TODO: fix assemble for intcomp and and/or - logic isn't quite right but will come back to it
class IntComp(ASTNode):
    def __init__(self, left: Expression | Int, right: Expression | Int, op: str):
        self.left = left
        self.right = right
        self.type = BOOL

        # make this a string with the name
        if isinstance(left.type, int):
            self.eval_type = node_types[left.type]
        else:
            self.eval_type = left.type

        if left.type != right.type:
            ASTError(TYPE, "Comparison can only be executed for same types.")

        if op in [">", "<", "==", "<=", ">="]:
            self.op = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def __str__(self):
        return f"IntComp: {self.left} {self.op} {self.right}, type = {self.eval_type}"
    
    def evaluate(self):
        if self.op[0] == "<":
            self.right.evaluate()
            self.left.evaluate()
        else:
            self.left.evaluate()
            self.right.evaluate()

        # this is <, > - only need to check one thing
        if len(self.op) == 1:
            with open(Obj.ASM_FILE, "a+") as f:
                print(f"\tcall {self.eval_type}:less", file=f)
            f.close()

        # if len = 2, either ==, which is one call..
        elif self.op == "==":
            with open(Obj.ASM_FILE, "a+") as f:
                print(f"\tcall {self.eval_type}:equals", file=f)
            f.close()

        # .. or <=, >=, which are combined into "less than or equals" with a boolean or
        elif len(self.op) == 2:
            op = BoolComp(IntComp(self.left, self.right, self.op[0]), IntComp(self.left, self.right, "=="), "or")
            op.evaluate()

        else:
            ASTError(SYNTAX, f"Error in parsing integer comparison operation. ")

class Not(ASTNode):
    def __init__(self, expr: IntComp | Bool):
        if isinstance(expr, IntComp):
            self.expr = IntComp(expr.right, expr.left, expr.op)
        elif isinstance(expr, BoolComp):
            self.expr = BoolComp(expr.right, expr.left, expr.op)
        else:
            ASTNode.error(TYPE, "Not can only be applied to boolean expressions.")

    def __str__(self):
        return f"Not: {self.expr}"

    def evaluate(self):
        # reverse control flow
        self.expr.evaluate()

class Assign(ASTNode):
    def __init__(self, var: Variable | str, val: Obj, declared_type: int = None):
        self.var = var
        self.val = val
        if declared_type is not None:
            self.type = declared_type
            if self.val.type != self.type:
                ASTError(TYPE, f"Declared variable type {node_types[self.type]} must match expression type {node_types[val.type]}.")

    def __str__(self):
        return f"Assign: {self.var}, {self.val}"
    
    def evaluate(self):
        self.val.evaluate()
        self.var.store()

class Return(ASTNode):
    def __init__(self, ret: Obj):
        self.ret = ret
    
    def __str__(self):
        return f"Return: {self.ret}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\treturn {self.ret}", file=f)
        f.close()

class IfNode(ASTNode):
    def __init__(self, cond: IntComp | BoolComp, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, f"Conditional statement <{self.cond}, {type(self.cond)}> must be a bool!")

    def __str__(self):
        return f"If: {self.cond}"
    
    def evaluate(self):
        pass


class ElifNode(ASTNode):
    def __init__(self, cond: Expression, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"Elif: {self.cond}"
    
    def evaluate(self):
        pass

class ElseNode(ASTNode):
    def __init__(self, block: Block):
        self.statement = block

    def __str__(self):
        return "Else: "
    
    def evaluate(self):
        self.statement.evaluate()


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
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tjump_if if_clause{iflabel}", file=f)
        f.close()
        eliflabels = []
        if self.elifnode is not None:
            for elf in self.elifnode:
                eliflabels.append(ASTNode.gen_elif_label())
                elf.cond.evaluate()
                with open(Obj.ASM_FILE, "a+") as f:
                    print(f"\tjump_if elif_clause{eliflabels[-1]}", file=f)
                f.close()

        if self.elsenode is not None:
            self.elsenode.evaluate()
            with open(Obj.ASM_FILE, "a+") as f:
                print(f"\tjump {block}", file=f)
            f.close()
        
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"if_clause{iflabel}:", file=f)
        f.close()
        self.ifnode.statement.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tjump {block}", file=f)
        f.close()

        for label, elf in zip(eliflabels, self.elifnode):
            with open(Obj.ASM_FILE, "a+") as f:
                print(f"if_clause{label}:", file=f)
            f.close()
            elf.statement.evaluate()
            with open(Obj.ASM_FILE, "a+") as f:
                print(f"\tjump {block}", file=f)
            f.close()

        with open(Obj.ASM_FILE, "a+") as f:
            print(f"{block}:", file=f)
        f.close()

class While(ASTNode):
    def __init__(self, cond: IntComp | BoolComp, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"While: ({self.cond}) {self.statement}"
    
    def evaluate(self):
        loop = ASTNode.gen_loop_label()
        with open(Obj.ASM_FILE, "a+") as f:
            # print(f"loop{loop}:", file=f)
            print(f"\tjump startl{loop}", file=f)
            print(f"startl{loop}:", file=f)
        f.close()
        self.cond = Not(self.cond)
        self.cond.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            # print(f"\tjump_if end_loop{loop}",  file=f)
            print(f"\tjump_if endl{loop}", file=f)
        f.close()
        self.statement.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tjump startl{loop}", file=f)
            print(f"endl{loop}:", file=f)
        f.close()

class Field(ASTNode):
    # field access of a class instance
    def __init__(self, var: Obj | ASTNode = None, expr: str = None):
        self.expr = expr
        self.var = var
        self.val = None
        self.type = OBJ

    def __str__(self):
        return f"{self.var}.{self.expr}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tload $\n\tload $:{self.var}", file=f)
        f.close()

    def store(self):
        if self.var.name == "this":
            this = "$"
        else:
            this = self.var

        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tload {this}\n\tstore_field {this}:{self.expr}", file=f)
        f.close()

    def assign(self, val, type):
        self.val = val
        self.type = type

    def set_var(self, var):
        self.var = var

# formal parameters for a method
class Params(ASTNode):
    def __init__(self, params: list[(str, str | int)] = []):
        self.params = params
    
    def add_param(self, new_param: tuple[str, str | int]):
        """
        Add a new argument to a method or class signature
        takes a tuple (name, type), where name the variable name and type is an int for built-in classes or str for user-defined classes
        """
        # skip this - reference to inherent class variable
        if new_param[0] != "this":
            self.params.append(new_param)

    def get_params(self):
        f = f"{self.params[0][0]}"
        for p in self.params[1:]:
            f += f",{p[0]}"
        return f

    def __str__(self):
        f = f""
        for p in self.params:
            f = f + f"{p[0]}: {p[1]},"
        return f[0:-1]

# TODO: fix assembly
class Method(ASTNode):
    def __init__(self, name: str, args: Params, ret: int, block: Block):
        self.name = name
        self.args = args
        # return type of method
        self.type = ret
        # statements
        self.block = block

        # TODO: check that return value is actual return value
        self.locals: list[Variable] = []

    def add_local(self, var: Variable) -> None:
        self.locals.append(var)

    def get_locals(self) -> str | None:
        if len(self.locals) == 1:
            return None
        f = f""
        for l in self.locals:
            f += f",{l.name}"
        return f[1:]

    def __str__(self):
        return f"Method: {self.name}({self.args}) -> {self.type}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            # print(f"loop{loop}:", file=f)
            print(f".method {self.name}", file=f)
            args = self.args.get_params()
            if args != f"":
                print(f"\t.local {self.args.get_params()}", file=f)
        f.close()
        self.block.evaluate()

class ClassBody(ASTNode):
    def __init__(self, statements: Block, methods: list[Method] = []):
        self.statements = statements
        self.methods = methods

    def __str__(self):
        return f"{self.methods}"
    
    def add_method(self, m: Method):
        self.methods.append(self)

    def evaluate(self):
        self.statements.evaluate()
        for method in self.methods:
            with open(Obj.ASM_FILE, "a+") as f:
                print(f"\n", file=f)
            f.close()
            method.evaluate()

class Class(ASTNode):
    # list of user-defined classes
    # name of class : class
    classes: dict[str: ASTNode] = {}

    def __init__(self, classname: str, constructor_args: Params = None, class_body: ClassBody = None, parent: int | str = OBJ):
        self.name = classname
        self.params = constructor_args
        self.class_body = class_body
        self.parent = parent
        
        self.fields = {}

        Class.classes[self.name] = self

    def __str__(self):
        return f"Class: {self.name} ({self.params}) -> {self.parent}"
    
    def get_methods(self):
        m = []
        for method in self.class_body.methods:
            m.append(method.name)
        return m
    
    def get_params(self):
        par = []
        for p in self.params.params:
            par.append(p[1])
        return par
    
    def add_local(self, var: Variable):
        self.fields[var.name] = var

    def evaluate(self):
        # check if it inherits a builtin class or a new class
        if isinstance(self.parent, int):
            inherit = node_types[self.parent]
        else:
            inherit = self.parent

        with open(Obj.ASM_FILE, "a+") as f:
            print(f".class {self.name}:{inherit}", file=f)
            print(f".method $constructor", file=f)
            # TODO: fields, forward declaration of methods
        f.close()
        self.class_body.evaluate()
        
class UserClassInstance(ASTNode):
    def __init__(self, class_type: str, constructor_args: list[Obj]):
        self.type = class_type
        self.args = constructor_args

        self.check_args()
    
    def check_args(self):
        c = Class.classes[self.type]
        for a, c in zip(self.args, c.get_params()):
            if a.type != c:
                ASTError(TYPE, f"Arguments to class instance do not match constructor.")

    def __str__(self):
        return f"Class instance: {self.type}({self.args})"
    
    def evaluate(self):
        for arg in self.args:
            arg.evaluate()
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tnew {self.type}\n\tcall {self.type}:$constructor", file=f)
        f.close()

# TODO: generalize to all calls
class Call(ASTNode):
    def __init__(self, var: Obj, method: str, args: Params):
        self.var = None
        self.type = None
        self.args = args
        if var is not None:
            self.var = var
            self.type = var.type

        self.method = method

    def assign_var(self, expr: Obj):
        self.var = expr
        self.type = expr.type

    def __str__(self):
        return f"Call: {self.var}.{self.method}()"
    
    def evaluate(self) -> None:
        """
        Eventually include type checking in this
        """
        calling = ""
        if self.type == INT:
            if self.method not in Int.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.type}")
            calling = "Int"
        elif self.type == OBJ:
            if self.method not in Obj.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.type}")
            calling = "Obj"
        elif self.type == BOOL:
            if self.method not in Bool.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.type}")
            calling = "Bool"
        elif self.type == STRING:
            if self.method not in String.methods:
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.type}")
            calling = "String"
        elif self.type == NOTHING:
            raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.type}")
        
        with open(Obj.ASM_FILE, "a") as f:
            self.var.evaluate()
            print(f"\tcall {calling}:{self.method}", file=f)
        f.close()