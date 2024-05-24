from quack_builtins import *

TYPE, SYNTAX = range(2)

def ASTError(which: int, msg: str):
    if which == TYPE:
        raise TypeError(f"ASTError: " + msg)
    elif which == SYNTAX:
        raise SyntaxError(f"ASTError: " + msg)
    exit(1)

class ASTNode():
    if_stmts = 0
    elif_stmts = 0
    else_stmts = 0
    loops = 0
    block_label = 0
    boolcomp_label = 0
    typecase_label = 0
    typecase_gen_label = 0

    def __init__(self):
        self.ret_type = NOTHING
    
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
    
    def gen_typecase_label():
        ret = f"{ASTNode.typecase_label}"
        ASTNode.typecase_label += 1
        return ret
    
    def gen_typecase_gen_label():
        ret = f"{ASTNode.typecase_gen_label}"
        ASTNode.typecase_gen_label += 1
        return ret

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
        ret = 1
        for s in self.statements:
            ret = s.evaluate()
            # if just calling and not returning anything, pop the result off the stack
            # if isinstance(s, Call):
            #     with open(Obj.ASM_FILE, "a+") as f:
            #         print("\tpop", file=f)
            #     f.close()
        # this should always return the value of the return statement
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
            self.type = left.type

        # operands can be any type but have to be the same
        if left.type != right.type:
            ASTError(TYPE, f"Operands must have same type, not {node_types[left.type]} and {node_types[right.type]}.")
        
        if op in "+-*/":
            self.token = op
            self.op = Expression.ops[op]
        # this shouldn't ever happen
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")

    def evaluate(self):
        self.left.evaluate()
        self.right.evaluate()

        # check that the operator is defined for the class
        # for built-ins, only Int is ok
        if isinstance(self.type, int):
            if self.type != INT:
                ASTError(TYPE, f"Op {self.op} undefined for class {node_types[self.type]}")
            t = node_types[self.type]
        else:
            if self.type not in Class.classes[self.type].get_methods():
                ASTError(TYPE, f"Op {self.op} undefined for class {self.type}")
            t = self.type

        # it would be better to have this as a call node but it works now 
        # and also is not my priority. so.

        # print to file
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tcall {t}:{self.op}", file=f)
        f.close()

    def __str__(self):
        return f"Expression: ({self.left} {self.token} {self.right})"

class BoolComp(ASTNode):
    def __init__(self, left: Expression | Int, right: Expression | Int, op: str):
        # and/or

        self.left = left
        self.right = right
        self.type = BOOL

        # check that both arguments are bools
        if right.type != BOOL or left.type != BOOL:
            ASTError(TYPE, f"And/Or Comparison can only be executed for Boolean values, not {node_types[self.left.type]}, {node_types[self.right.type]}.")

        if op in ["and", "or"]:
            self.op = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def __str__(self):
        return f"BoolComp: {self.left} <{self.op}> {self.right}"
    
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
        # this actually has nothing to do with 
        if self.op == "or":
            self.eval_or()
        elif self.op == "and":
            self.eval_and()

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
        return f"IntComp: {self.left} _{self.op}_ {self.right}, eval_type = {self.eval_type}"
    
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
            ASTError(TYPE, "Not can only be applied to boolean expressions.")

    def __str__(self):
        return f"Not: {self.expr}"

    def evaluate(self):
        # reverse control flow
        self.expr.evaluate()

class Assign(ASTNode):
    def __init__(self, var: Variable, val: Obj | ASTNode, declared_type: int = None):
        self.var = var
        self.val = val
        if declared_type is not None:
            self.type = declared_type
            if self.val.type != self.type:
                ASTError(TYPE, f"Declared variable type {node_types[self.type]} must match expression type {node_types[val.type]}.")
        elif isinstance(val, Call):
            self.type = val.type
            var.type = self.type
        else:
            self.type = self.var.type
        
    def set_type(self, t):
        self.type = t
        self.var.type = t

    def __str__(self):
        return f"Assign: {self.var}, {self.val} <{self.type}>"
    
    def evaluate(self):
        self.val.evaluate()
        self.var.store()

class Return(ASTNode):
    def __init__(self, ret: Obj | ASTNode):
        self.ret = ret
    
    def __str__(self):
        return f"Return: {self.ret}"
    
    def evaluate(self):
        if self.ret is not None:
            self.ret.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\treturn ", file=f, end="")
        f.close()
        if self.ret is None:
            return
        return self.ret.type

class IfNode(ASTNode):
    def __init__(self, cond: IntComp | BoolComp, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, f"Conditional statement <{self.cond}, {type(self.cond)}> must be a bool!")

    def __str__(self):
        return f"If: {self.cond}, [{self.statement}]"
    
    def evaluate(self):
        pass


class ElifNode(ASTNode):
    def __init__(self, cond: Expression, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"Elif: {self.cond} [{self.statement}]"
    
    def evaluate(self):
        pass

class ElseNode(ASTNode):
    def __init__(self, block: Block):
        self.statement = block

    def __str__(self):
        return f"Else: [{self.statement}]"
    
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
                print(f"elif_clause{label}:", file=f)
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
        return f"While: {self.cond} [{self.statement}]"
    
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
    def __init__(self, belongs: Obj | ASTNode = None, field: str | Variable = None):
        # expression/assignemnt
        self.field = field
        # name of variable
        self.belongs = belongs
        self.val = None

        self.type = OBJ

        if isinstance(field, Variable):
            self.type = field.type

    def __str__(self):
        return f"Field: {self.belongs}.{self.field}, <{self.type}>"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tload $\n\tload_field $:{self.field}", file=f)
        f.close()

    def store(self):
        if self.belongs.name == "this":
            this = "$"
        else:
            this = self.belongs

        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tload {this}\n\tstore_field {this}:{self.field}", file=f)
        f.close()

    def assign(self, val: Obj | ASTNode, type = None):
        self.val = val
        self.type = type
        if type is None:
            self.type = val.type

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

    def get_param_names(self):
        if self.params != []:
            f = f"{self.params[0][0]}"
            for p in self.params[1:]:
                f += f",{p[0]}"
            return f
        return f""
    
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

        # TODO: check that return value is actual return value
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
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            # print(f"loop{loop}:", file=f)
            print(f"\n.method {self.name}", file=f)
            args = self.args.get_param_names()
            if args != f"":
                print(f".args {args}", file=f)
            # k = list(self.locals.keys())
            # if k is not None:
            #     print(f".local {self.get_locals()}", file=f)
            print("\tenter", file=f)
        f.close()
        ret = self.block.evaluate()
        with open(Obj.ASM_FILE, "+a") as f:
            print(f"{len(self.args.get_params())}", file=f)
        if ret is None and self.type == NOTHING:
            return
        if ret != self.type:
            t = self.type
            if isinstance(self.type, int):
                t = node_types[self.type]
            if isinstance(ret, int):
                ret = node_types[ret]
            ASTError(TYPE, f"Return value of {ret} does not matched declared return value {t}")


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

    def evaluate(self, l):
        self.statements.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print(f"\tload $\n\treturn {l}", file=f)
        f.close()
        for method in self.methods:
            method.evaluate()

class Class(ASTNode):
    # list of user-defined classes
    # name of class : class
    classes: dict[str: ASTNode] = {}

    def __init__(self, classname: str, constructor_args: Params | list = None, class_body: ClassBody = None, parent: int | str = OBJ):
        self.name = classname

        if isinstance(constructor_args, list):
            constructor_args = Params(constructor_args)

        self.params = constructor_args
        self.class_body = class_body
        self.parent = parent
        
        self.fields: dict[str: type] = {}

        Class.classes[self.name] = self

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

    def evaluate(self):
        # check if it inherits a builtin class or a new class
        if isinstance(self.parent, int):
            inherit = node_types[self.parent]
        else:
            inherit = self.parent

        Obj.ASM_FILE = f"{self.name}.asm"

        with open(Obj.ASM_FILE, "w+") as f:
            print(f".class {self.name}:{inherit}", file=f)
            for field in self.fields.keys():
                print(f".field {field}", file=f)

            for m in self.class_body.methods:
                print(f".method {m.name} forward", file=f)
            print(f"\n.method $constructor", file=f)
            if self.params.params != []:
                print(f".args ", file=f, end="")
                print(f"{self.params.get_param_names()}\n\tenter", file=f)
            else:
                print("\tenter", file=f)
            # TODO: forward declaration of methods
        f.close()

        # shoudn't have a return?
        self.class_body.evaluate(len(self.get_params()))
        
        
class UserClassInstance(ASTNode):
    def __init__(self, class_type: str, constructor_args: list[Obj]):
        self.type = class_type
        self.args = constructor_args

        self.check_args()
    
    def check_args(self):
        try:
            c = Class.classes[self.type]
        except:
            ASTError(SYNTAX, f"Class <{self.type}> is undefined.")

        if len(c.get_params()) == len(self.args) and c.get_params() != []:
            for a, c in zip(self.args, c.get_params()):
                if a.type != c:
                    ASTError(TYPE, f"Type {a.type} does not match constructor type {c}")
        elif len(self.args) != 0:
            ASTError(SYNTAX, f"{self.type} constructor takes {len(c.get_params())} arguments but {len(self.args)} were given.")


    def __str__(self):
        return f"User class instance: {self.type}({self.args})"
    
    def evaluate(self):
        for arg in self.args:
            arg.evaluate()
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tnew {self.type}\n\tcall {self.type}:$constructor", file=f)
        f.close()

class TypecaseCase(ASTNode):
    def __init__(self, test, test_type, statement: Block):
        self.name = test
        self.type = test_type
        self.statements = statement
    
    def __str__(self):
        return f"{self.name} : {self.type} [{self.statements}]"
    
    def evaluate_check(self, label):
        if isinstance(self.type, int):
            t = node_types[self.type]
        else:
            t = self.type
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tis_instance {t}", file=f)
            print(f"\tjump_if it_is{label}", file=f)
        f.close()

    def evaluate_block(self, label, tl):
        with open(Obj.ASM_FILE, "a") as f:
            print(f"it_is{label}:", file=f)
        f.close()
        self.statements.evaluate()
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tjump next{tl}", file=f)
        f.close()

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
            with open(Obj.ASM_FILE, "a") as f:
                print(f"\tload {self.test}", file=f)
            f.close()
            c.evaluate_check(label)
        
        for c, l in zip(self.cases, labels):
            c.evaluate_block(l, tl)
        
        with open(Obj.ASM_FILE, "a") as f:
            print(f"next{tl}:", file=f)
        f.close()
        

# TODO: generalize to all calls
class Call(ASTNode):
    def __init__(self, var: Obj | ASTNode = None, method: str = None, args: Params = None):
        self.var = var
        self.ret_type = None
        self.type = None

        self.args = args
        if var is not None:
            self.type = var.type

        self.method = method

        self.ret_type = None

        if self.type is not None:
            self.check_method()

        self.check_args()

    def check_args(self):
        # builtins which take no arguments
        if self.method in ["print", "string"]:
            if self.args is not None and len(self.args) != 0:
                ASTError(SYNTAX, f"Method {self.method} takes 0 arguments, {len(self.args.get_params())} given.")
        elif self.method in ["equals", "less", "add", "minus", "times", "divide"]:
            p = self.args
            if self.args is None or len(p) > 1 or len(p) == 0:
                ASTError(SYNTAX, f"Method {self.method} takes 1 arguments, {len(self.args.get_params())} given.")
            elif p[0].type != self.type:
                ASTError(TYPE, f"Argument type {p[0].type} must match calling type {self.type} for method {self.method}.")

    def check_method(self):
        if isinstance(self.type, str):
            ms = Class.classes[self.type].get_methods()
            try:
                self.ret_type = ms[self.method].type
            except:
                # ASTError(SYNTAX, f"Method {self.method} does not exist for type {self.type}")
                self.type = Class.classes[self.type].parent
                self.check_method()
                return
        else:
            if self.type == INT:
                if self.method in ["less", "equals"]:
                    self.ret_type = BOOL
                elif self.method in ["plus", "minus", "times", "divide"]:
                    self.ret_type = INT
            else:
                if self.method in ["equals"]:
                    self.ret_type = BOOL
                elif self.method in ["string"]:
                    self.ret_type = STRING
        return 

    def assign_var(self, expr: Obj | ASTNode):
        self.var = expr
        self.type = expr.type
        self.check_method()

    def __str__(self):
        return f"Call: {self.var}<{self.type}>.{self.method}({self.args}), ret_type={self.ret_type}"
    
    def evaluate(self) -> None:
        """
        Eventually include type checking in this
        """
        calling = ""

        # for built-in funcs - make lower in assembly
        if isinstance(self.type, str):
            ms = Class.classes[self.type].get_method_names()
            try:
                if self.method in ms:
                    self.method = self.method.lower()
            except:
                ASTError(SYNTAX, f"Method {self.method} does not exist for type {self.type}")
            
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
        elif isinstance(self.type, str):
            if self.method not in Class.classes[self.type].get_method_names():
                raise Exception(f"Invalid method call on {self.var}: {self.method} does not exist for type {self.type}")
            calling = self.type
        
        for arg in self.args:
            arg.evaluate()
        with open(Obj.ASM_FILE, "a") as f:
            self.var.evaluate()
            print(f"\tcall {calling}:{self.method}", file=f)
        f.close()