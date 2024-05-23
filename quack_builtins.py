# define node types for tree
OBJ, INT, NEGINT, STRING, BOOL, NOTHING = range(6)
node_types = {OBJ: "Obj", INT: "Int", NEGINT: "Negint", STRING: "String", BOOL: "Bool", NOTHING: "Nothing"}
var_types = {"Obj": OBJ, "Int": INT, "String": STRING, "Boolean": BOOL, "Nothing": NOTHING}
keywords = r"class|if|while|and|typecase|def|elif|return|or|not|extends|else|String|Int|Obj|Boolean|true|false|Nothing|none"

class Obj():
    ASM_FILE = "out.asm"

    # list of methods for the Obj class
    methods: list[str] = ["string", "print", "equals"]

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
    methods: list[str] = ["string", "print", "equals", "plus", "minus", "times", "divide", "less"]

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
    methods: list[str] = ["print", "string", "and", "or"]

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
                print(f"\tconst true", file=f)
            else:
                print(f"\tconst false", file=f)
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

    def assign(self, value, type):
        self.val = value
        self.type = type
    
    def display(self):
        return f"{self.name} = ({node_types[self.type]}, {self.val})"
    
    def __str__(self):
        return f"{self.name}"

    def store(self) -> None:
        with open(Obj.ASM_FILE, "a") as f:
            print(f"\tstore {self.name}", file=f)
        f.close()

    def evaluate(self) -> None:
        if self in Variable.expr:
            with open(Obj.ASM_FILE, "a") as f:
                print(f"\tload {self.name}", file=f)
            f.close()
        else:
            raise Exception(f"Call to unassigned variable {self.name}")