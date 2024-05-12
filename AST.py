from quack_builtins import *

TYPE, SYNTAX = range(2)

def ASTError(which: int, msg: str):
    if which == TYPE:
        raise TypeError(msg)
    elif which == SYNTAX:
        raise SyntaxError(msg)

class ASTNode():
    def __init__(self):
        self.type = NOTHING

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
            self.token = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def __str__(self):
        return f"IntComp: {self.left} {self.token} {self.right}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tSTART INTCOMP", file=f)
        f.close()
        self.left.evaluate()
        self.right.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tEND INTCOMP", file=f)
        f.close()

class BoolComp(ASTNode):
    def __init__(self, left: Expression | Int, right: Expression | Int, op: str):
        self.left = left
        self.right = right
        self.type = BOOL

        if right.type != BOOL or left.type != BOOL:
            ASTError(TYPE, "Comparison can only be executed for Boolean values.")

        if op in ["and", "or"]:
            self.token = op
        else:
            raise SyntaxError(f"op {op} does not exist in Quack!")
        
    def __str__(self):
        return f"BoolComp: {self.left} {self.token} {self.right}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tSTART BOOLCOMP", file=f)
        f.close()
        self.left.evaluate()
        self.right.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tEND BOOLCOMP", file=f)
        f.close()

# TODO
class Not(ASTNode):
    def __init__(self, expr: IntComp | Bool):
        self.expr = expr
    
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
            print(f"\tcall {calling}:{self.method}", file=f)
        f.close()

class IfNode(ASTNode):
    def __init__(self, cond: Expression, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"If: {self.cond}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tSTART IF", file=f)
        f.close()
        self.cond.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tcmp 0", file=f)
        f.close()
        self.statement.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tEND IF", file=f)
        f.close()


class ElifNode(ASTNode):
    def __init__(self, cond: Expression, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"Elif: {self.cond}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tSTART ELIF", file=f)
        f.close()
        self.cond.evaluate()
        self.statement.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tEND ELIF", file=f)
        f.close()

class ElseNode(ASTNode):
    def __init__(self, block: Block):
        self.statement = block

    def __str__(self):
        return "Else: "
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tSTART ELSE", file=f)
        f.close()
        self.statement.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tEND ELSE", file=f)
        f.close()


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
        self.ifnode.evaluate()
        if self.elifnode is not None:
            for elf in self.elifnode:
                elf.evaluate()
        if self.elsenode is not None:
            self.elsenode.evaluate()

class While(ASTNode):
    def __init__(self, cond: Expression, block: Block):
        self.statement = block
        self.cond = cond

        if cond.type != BOOL:
            ASTError(TYPE, "Conditional statement must be a bool!")

    def __str__(self):
        return f"While: ({self.cond}) {self.statement}"
    
    def evaluate(self):
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tSTART WHILE", file=f)
            print("loop:", file=f)
        f.close()
        self.cond.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tjmp end", file=f)
        f.close()
        self.statement.evaluate()
        with open(Obj.ASM_FILE, "a+") as f:
            print("\tjmp start", file=f)
            print("\tEND WHILE", file=f)
        f.close()
        