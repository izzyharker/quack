from quack_builtins import *

TYPE, SYNTAX = range(2)

def ASTError(which: int, msg: str):
    if which == TYPE:
        raise TypeError(msg)
    elif which == SYNTAX:
        raise SyntaxError(msg)

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
        ret = f"{ASTNode.boolcomp_label}"
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
    # specifically for Int classes
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

# come back to this - not sure what the assemble is supposed to look like
class IntComp(ASTNode):
    def __init__(self, left: Expression | Int, right: Expression | Int, op: str):
        self.left = left
        self.right = right
        self.type = BOOL

        if left.type != right.type or left.type != INT:
            ASTError(TYPE, "Comparison can only be executed for Int/Int.")

        if op in [">", "<", "==", "<=", ">="]:
            self.op = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def __str__(self):
        return f"IntComp: {self.left} {self.op} {self.right}"
    
    def get_first_function(self):
        if self.op in ["<", ">"]:
            return "less"
        elif self.op == "==":
            return "equals"
        else:
            return None
    
    def evaluate(self):
        if self.op == "<":
            self.right.evaluate()
            self.left.evaluate()
        else:
            self.left.evaluate()
            self.right.evaluate()

        func = self.get_first_function()
        if func is not None:
            with open(Obj.ASM_FILE, "a+") as f:
                print(f"\tcall Int:{func}", file=f)
            f.close()

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
    
    def evaluate(self):
        self.left.evaluate()
        self.right.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tcall Bool:equals", file=f)
        f.close()

class Not(ASTNode):
    def __init__(self, expr: IntComp | Bool):
        if isinstance(expr, IntComp):
            self.expr = IntComp(expr.right, expr.left, expr.op)
        elif isinstance(expr, BoolComp):
            self.expr = BoolComp(expr.right, expr.left, expr.op)
        else:
            ASTNode.error(TYPE, "Not can only be applied to boolean expressions.")

    def __str__(self):
        return f"{self.expr}"

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

class Call(ASTNode):
    def __init__(self, var: Obj, method: str):
        self.var = None
        self.type = None
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
            print(f"\tcall {calling}:{self.method}\n\tpop", file=f)
        f.close()

class IfNode(ASTNode):
    def __init__(self, cond: IntComp | BoolComp, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, "Conditional statement must be a bool!")

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
            # print(f"\tjump {loop}", file=f)
            print(f"\tjump startl{loop}", file=f)
            # print(f"end_loop{loop}:", file=f)
            print(f"endl{loop}:", file=f)
        f.close()
        