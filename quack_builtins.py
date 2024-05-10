# define node types for tree
OBJ, INT, NEGINT, STRING, BOOL, NOTHING = range(6)
node_types = {OBJ: "OBJ", INT: "INT", NEGINT: "NEGINT", STRING: "STRING", BOOL: "BOOL", NOTHING: "NOTHING"}
var_types = {"Obj": OBJ, "Int": INT, "String": STRING, "Boolean": BOOL}
keywords = r"class|if|while|and|typecase|def|elif|return|or|not|extends|else|String|Int|Obj|Boolean|true|false|Nothing|none"


class Obj():
    ASM_FILE = "out.asm"

    # list of methods for the Obj class
    methods: list[str] = []

    def __init__(self, value: None):
        self.val = value
        self.type = OBJ

    def get_type(self) -> int:
        return self.type

    def evaluate(self):
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tconst {self.val}", file=f)
        f.close()
        # print(f"\tconst {self.val}")
    
    def __str__(self):
        return f"{self.val}"

class Int(Obj):
    # list of methods for the Int class
    methods: list[str] = ["print", "plus", "minus", "times", "divide"]

    def __init__(self, value: int):
        super().__init__(value)
        self.val = value
        self.type = INT

    def evaluate(self):
        with open(Obj.ASM_FILE, "a") as f:
            if self.val < 0:
                print(f"\tconst 0", file=f)
                print(f"\tconst {abs(self.val)}", file=f)
                print(f"\tcall Int:minus", file=f)
            else:
                print(f"\tconst {self.val}", file=f)
        f.close()
            
# class NegInt(Obj):
#     def __init__(self, value: int):
#         super().__init__(value)
#         self.val = abs(value)
#         self.type = INT

class String(Obj):
    # list of methods for the String class
    methods: list[str] = ["print"]

    def __init__(self, value: str):
        super().__init__(value)
        self.val = value
        self.type = STRING

class Bool(Obj):
    # list of methods for the Bool class
    methods: list[str] = []

    def __init__(self, value: str):
        super().__init__(value)
        if value == "True" or value == "true":
            self.val = True
        else:
            self.val = False

        self.type = BOOL

    def evaluate(self):
        with open(Obj.ASM_FILE, "a") as f:
            if self.val:
                print(f"\tconst 1", file=f)
            else:
                print(f"\tconst 0", file=f)
        f.close()

class Nothing(Obj):
    # list of methods for the Obj class
    methods: list[str] = []

    def __init__(self):
        super().__init__(None)
        self.val = None
        self.type = NOTHING

class Variable(Obj):
    # vars: 
    # name: (type, number in sequence)
    expr: list[Obj] = []
    var_names: list[str] = []
    var_index = 0

    def __init__(self, name: str, given_type: str, value: Obj):
        self.name = name
        self.val = value
        self.type = given_type

        Variable.expr.append(self)
        if self.name not in Variable.var_names:
            Variable.var_names.append(self.name)
        Variable.var_index += 1

    def get_type(self) -> int:
        return self.type
    
    def __str__(self):
        return f"{self.name}: {node_types[self.type]}"
    
    def store(self) -> None:
        self.val.evaluate()
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tstore {self.name}", file=f)
        f.close()

    def evaluate(self) -> None:
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tload {self.name}", file=f)
        f.close()

class Operator(Obj):
    # operator tree
    ops = {"+": "plus", "-": "minus", "*": "multiply", "/": "divide"}

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
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tcall Int:{self.op}", file=f)
        f.close()
        # print(f"\tcall Int:{Operator.ops[self.op]}")
        
        pass

    def __str__(self):
        return f"({self.left} {self.token} {self.right})"
    
class Call():
    def __init__(self, var: Obj, method: str):
        self.var = var
        self.type = var.type
        self.method = method

    def __str__(self):
        return f"{self.var}.{self.method}()"
    
    def evaluate(self) -> None:
        """
        Need to fix this for variables
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
            print(f"\tconst {self.var}", file = f)
            print(f"\tcall {calling}:{self.method}", file=f)
        f.close()
